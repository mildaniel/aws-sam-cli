variable "rest_api_name" {
    type = string
    default = "module_rest_api"
}

variable "unauthenticated_function" {
    type = string
}

variable "authenticated_function" {
    type = string
}

variable "autherizer_function" {
    type = string
}

resource "random_uuid" "unique_id" {
    keepers = {
        my_key = "my_key"
    }
}

variable "ValidationString" {
  type    = string
  default = ""
}

resource "aws_iam_role" "invocation_role" {
  name = "iam_lambda_${random_uuid.unique_id.result}"
  path = "/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_apigatewayv2_api" "http_api" {
  name           = "http_api"
  protocol_type  = "HTTP"
}

resource "aws_apigatewayv2_deployment" "http_api" {
  api_id      = aws_apigatewayv2_api.http_api.id
  depends_on  = [
    aws_apigatewayv2_integration.unauthenticated_function_resource_integration,
    aws_apigatewayv2_integration.auth_integration,
    aws_apigatewayv2_route.unauthenticated_function_route,
    aws_apigatewayv2_route.header_root_function_resource_get_route,
    aws_apigatewayv2_route.request_function_route,
  ]
}

resource "aws_apigatewayv2_stage" "http_api" {
  api_id          = aws_apigatewayv2_api.http_api.id
  deployment_id   = aws_apigatewayv2_deployment.http_api.id
  name            = "example-stage-${random_uuid.unique_id.result}"
}

resource "aws_apigatewayv2_route" "unauthenticated_function_route" {
  api_id         = aws_apigatewayv2_api.http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.unauthenticated_function_resource_integration.id}"
  route_key      = "GET /unauthenticated_module_api"
  operation_name = "unauthenticated_function_route"
  depends_on = [aws_apigatewayv2_integration.unauthenticated_function_resource_integration]
}

resource "aws_apigatewayv2_integration" "unauthenticated_function_resource_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = var.unauthenticated_function
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "auth_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = var.authenticated_function
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "header_root_function_resource_get_route" {
  api_id         = aws_apigatewayv2_api.http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
  route_key      = "GET /header_function"
  operation_name = "header_root_function_resource_get_route"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.header_authorizer.id
  depends_on = [aws_apigatewayv2_integration.auth_integration]
}

resource "aws_apigatewayv2_authorizer" "header_authorizer" {
  api_id           = aws_apigatewayv2_api.http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = var.autherizer_function
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader"]
  name             = "header_authorizer"
}

resource "aws_apigatewayv2_route" "request_function_route" {
  api_id         = aws_apigatewayv2_api.http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
  route_key      = "GET /request_function"
  operation_name = "header_root_function"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.root_request_authorizer.id
}

resource "aws_apigatewayv2_authorizer" "root_request_authorizer" {
  api_id           = aws_apigatewayv2_api.http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = var.autherizer_function
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader", "$request.querystring.mystring"]
  name             = "request_authorizer"
}
