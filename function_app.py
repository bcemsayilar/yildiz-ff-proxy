import azure.functions as func
import logging
import requests
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# FF Data API base URL (AWS - private endpoint)
FF_DATA_BASE_URL = "https://api-gateway-external-ff-auth.test.ff.ceptesok.com"

@app.route(route="ff-proxy/employee-candidate/{id}", methods=["GET"])
def get_candidate_details(req: func.HttpRequest) -> func.HttpResponse:
    """
    Proxy for GET /ai/employee-candidate/{id}
    Forwards request to AWS FF endpoint
    """
    candidate_id = req.route_params.get('id')
    logging.info(f'FF Proxy - GetCandidateDetails called for id: {candidate_id}')

    # Get Authorization header from request
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        return func.HttpResponse(
            json.dumps({"error": "Authorization header is required"}),
            status_code=401,
            mimetype="application/json"
        )

    # Build target URL
    target_url = f"{FF_DATA_BASE_URL}/ai/employee-candidate/{candidate_id}"
    logging.info(f'FF Proxy - Forwarding to: {target_url}')

    try:
        # Forward request to AWS
        response = requests.get(
            target_url,
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            timeout=30
        )

        logging.info(f'FF Proxy - Response status: {response.status_code}')

        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            mimetype="application/json"
        )

    except requests.exceptions.Timeout:
        logging.error('FF Proxy - Request timeout')
        return func.HttpResponse(
            json.dumps({"error": "Request timeout to FF endpoint"}),
            status_code=504,
            mimetype="application/json"
        )
    except requests.exceptions.ConnectionError as e:
        logging.error(f'FF Proxy - Connection error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Connection error: {str(e)}"}),
            status_code=502,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f'FF Proxy - Unexpected error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Unexpected error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="ff-proxy/employee-candidate", methods=["PUT"])
def update_candidate_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    Proxy for PUT /ai/employee-candidate
    Forwards request to AWS FF endpoint
    """
    logging.info('FF Proxy - UpdateCandidateStatus called')

    # Get Authorization header from request
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        return func.HttpResponse(
            json.dumps({"error": "Authorization header is required"}),
            status_code=401,
            mimetype="application/json"
        )

    # Get request body
    try:
        request_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )

    # Build target URL
    target_url = f"{FF_DATA_BASE_URL}/ai/employee-candidate"
    logging.info(f'FF Proxy - Forwarding to: {target_url}')

    try:
        # Forward request to AWS
        response = requests.put(
            target_url,
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            json=request_body,
            timeout=30
        )

        logging.info(f'FF Proxy - Response status: {response.status_code}')

        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            mimetype="application/json"
        )

    except requests.exceptions.Timeout:
        logging.error('FF Proxy - Request timeout')
        return func.HttpResponse(
            json.dumps({"error": "Request timeout to FF endpoint"}),
            status_code=504,
            mimetype="application/json"
        )
    except requests.exceptions.ConnectionError as e:
        logging.error(f'FF Proxy - Connection error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Connection error: {str(e)}"}),
            status_code=502,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f'FF Proxy - Unexpected error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Unexpected error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    return func.HttpResponse(
        json.dumps({"status": "healthy", "service": "ff-data-proxy"}),
        status_code=200,
        mimetype="application/json"
    )
