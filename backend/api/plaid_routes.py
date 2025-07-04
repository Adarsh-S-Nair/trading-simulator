from fastapi import APIRouter, HTTPException, Header
from services.plaid_service import PlaidService
from services.supabase_service import get_supabase_service
from models.plaid_schema import (
    LinkTokenRequest, LinkTokenResponse,
    PublicTokenRequest, TokenExchangeResponse,
    AccountsResponse, SandboxCredentialsResponse
)
import os
from typing import Optional

router = APIRouter(prefix="/plaid", tags=["plaid"])

@router.post("/create-link-token", response_model=LinkTokenResponse)
async def create_link_token(request: LinkTokenRequest, authorization: Optional[str] = Header(None)):
    """
    Create a link token for the Plaid Link flow
    """
    # Use sandbox environment for development
    plaid_service = PlaidService(environment='sandbox')
    
    result = plaid_service.create_link_token(
        user_id=request.user_id,
        client_name=request.client_name
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return LinkTokenResponse(**result)

@router.post("/exchange-public-token", response_model=TokenExchangeResponse)
async def exchange_public_token(request: PublicTokenRequest, authorization: Optional[str] = Header(None)):
    """
    Exchange a public token for an access token
    """
    # For now, we'll use sandbox as default since we don't have user_id in this endpoint
    # In a real implementation, you'd get user_id from the authorization header
    plaid_service = PlaidService(environment='sandbox')
    
    result = plaid_service.exchange_public_token(request.public_token)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return TokenExchangeResponse(**result)

@router.post("/accounts", response_model=AccountsResponse)
async def get_accounts(request: PublicTokenRequest, user_id: str, authorization: Optional[str] = Header(None)):
    """
    Get accounts for a given public token and store them in the database
    """
    # Use sandbox environment for development
    supabase_service = get_supabase_service()
    user_environment = 'sandbox'  # Default to sandbox for development
    
    # Create Plaid service with user's environment
    plaid_service = PlaidService(environment=user_environment)
    
    # First exchange the public token for an access token
    exchange_result = plaid_service.exchange_public_token(request.public_token)
    
    if not exchange_result["success"]:
        raise HTTPException(status_code=400, detail=exchange_result["error"])
    
    # Then get the accounts using the access token
    accounts_result = plaid_service.get_accounts(exchange_result["access_token"])
    
    if not accounts_result["success"]:
        raise HTTPException(status_code=400, detail=accounts_result["error"])
    
    # Add access token to each account for storage
    access_token = exchange_result["access_token"]
    accounts_with_token = []
    for account in accounts_result["accounts"]:
        account_with_token = account.copy()
        account_with_token["access_token"] = access_token
        accounts_with_token.append(account_with_token)
    
    # Store the accounts in the database (access token is now included with each account)
    accounts_store_result = supabase_service.store_plaid_accounts(
        user_id=user_id,
        item_id=exchange_result["item_id"],
        accounts=accounts_with_token,
        environment=user_environment,
        access_token=access_token
    )
    
    if not accounts_store_result["success"]:
        print(f"Warning: Failed to store accounts: {accounts_store_result.get('error')}")
    
    # Fetch and store transactions for the new accounts
    try:
        # Get account IDs for transaction fetching
        account_ids = [account["account_id"] for account in accounts_result["accounts"]]
        
        # Fetch transactions (last 2 years by default)
        transactions_result = plaid_service.get_transactions(
            access_token=access_token,
            account_ids=account_ids,
            days_back=730  # 2 years
        )
        
        if transactions_result["success"] and transactions_result["transactions"]:
            # Store transactions in database
            transactions_store_result = supabase_service.store_transactions(
                transactions_result["transactions"]
            )
            
            if transactions_store_result["success"]:
                print(f"Successfully stored {transactions_store_result.get('stored_count', 0)} transactions")
            else:
                print(f"Warning: Failed to store transactions: {transactions_store_result.get('error')}")
        else:
            print(f"No transactions found or error fetching transactions: {transactions_result.get('error', 'No transactions')}")
            
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        # Don't fail the entire request if transaction fetching fails
    
    return AccountsResponse(**accounts_result)



@router.get("/sandbox-credentials", response_model=SandboxCredentialsResponse)
async def get_sandbox_credentials():
    """
    Get test credentials for sandbox mode
    """
    plaid_service = PlaidService(environment='sandbox')
    credentials = plaid_service.get_sandbox_test_credentials()
    
    if not credentials["success"]:
        raise HTTPException(status_code=400, detail=credentials["error"])
    
    return SandboxCredentialsResponse(**credentials) 