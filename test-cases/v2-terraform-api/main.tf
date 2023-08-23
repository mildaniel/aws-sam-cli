provider "aws" {
}

resource "random_uuid" "unique_id" {
    keepers = {
        my_key = "my_key"
    }
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

resource "aws_iam_role" "iam_for_lambda" {
  name = "dummy_iam_role_${random_uuid.unique_id.result}"

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

variable "HELLO_FUNCTION_SRC_CODE" {
  type    = string
  default = "./artifacts/HelloWorldFunction/function.zip"
}

variable "AuthHandler" {
  type    = string
  default = "app.auth_handler"
}


variable "ValidationString" {
  type    = string
  default = ""
}


locals {
  hello_world_function_src_path  = var.HELLO_FUNCTION_SRC_CODE
  layer1_src_path                = "./artifacts/layer1/layer1.zip"
}

resource "aws_lambda_layer_version" "layer1" {
  count               = 1
  filename            = local.layer1_src_path
  layer_name          = "lambda_layer1"
  compatible_runtimes = ["python3.8"]
}

## function defined in root module
resource "aws_lambda_function" "function1" {
  filename      = local.hello_world_function_src_path
  handler       = "app.unauthenticated_lambda_handler"
  runtime       = "python3.8"
  function_name = "function1"
  timeout       = 300
  role          = aws_iam_role.iam_for_lambda.arn
  layers = [
    aws_lambda_layer_version.layer1[0].arn,
  ]
}

resource "aws_lambda_function" "authorized_function1" {
  filename      = local.hello_world_function_src_path
  handler       = "app.lambda_handler"
  runtime       = "python3.8"
  function_name = "authorized_function1"
  timeout       = 300
  role          = aws_iam_role.iam_for_lambda.arn
  layers = [
    aws_lambda_layer_version.layer1[0].arn,
  ]
}

resource "aws_lambda_function" "authorizer1" {
  filename      = local.hello_world_function_src_path
  handler       = var.AuthHandler
  runtime       = "python3.8"
  function_name = "authorizer1"
  timeout       = 300
  role          = aws_iam_role.iam_for_lambda.arn
  layers = [
    aws_lambda_layer_version.layer1[0].arn,
  ]
}

## function defined in module

module "function2" {
  source        = "./lambda_function"
  source_code   = local.hello_world_function_src_path
  function_name = "function2"
  authorized_function_name = "authorized_function2"
  authorizer_function_name = "authorizer2"
  AuthHandler = var.AuthHandler
  layers        = [aws_lambda_layer_version.layer1[0].arn]
}

# serverless.tf 3rd party function
module "function7" {
  source                   = "terraform-aws-modules/lambda/aws"
  version                  = "4.6.0"
  timeout                  = 300
  local_existing_package   = local.hello_world_function_src_path
  function_name            = "function7"
  create_package           = false
  handler                  = "app.unauthenticated_lambda_handler"
  runtime                  = "python3.8"
  role_name                = "function7_role_${random_uuid.unique_id.result}"
  layers                   = [aws_lambda_layer_version.layer1[0].arn]
}

module "authorized_function7" {
  source                   = "terraform-aws-modules/lambda/aws"
  version                  = "4.6.0"
  timeout                  = 300
  local_existing_package   = local.hello_world_function_src_path
  function_name            = "authorized_function7"
  create_package           = false
  handler                  = "app.lambda_handler"
  runtime                  = "python3.8"
  role_name                = "authorized_function7_role_${random_uuid.unique_id.result}"
  layers                   = [aws_lambda_layer_version.layer1[0].arn]
}

module "authorizer7" {
  source                   = "terraform-aws-modules/lambda/aws"
  version                  = "4.6.0"
  timeout                  = 300
  local_existing_package   = local.hello_world_function_src_path
  function_name            = "authorizer7"
  create_package           = false
  handler                  = var.AuthHandler
  runtime                  = "python3.8"
  role_name                = "authorizer7_role_${random_uuid.unique_id.result}"
  layers                   = [aws_lambda_layer_version.layer1[0].arn]
}


resource "aws_apigatewayv2_api" "root_http_api" {
  name           = "root_http_api"
  protocol_type  = "HTTP"
}

resource "aws_apigatewayv2_deployment" "root_http_api" {
  api_id      = aws_apigatewayv2_api.root_http_api.id
  depends_on = [aws_apigatewayv2_integration.unauthenticated, aws_apigatewayv2_route.unauthenticated]
}

resource "aws_apigatewayv2_stage" "root_http_api" {
  api_id          = aws_apigatewayv2_api.root_http_api.id
  deployment_id = aws_apigatewayv2_deployment.root_http_api.id
  name            = "example-stage-${random_uuid.unique_id.result}"
}

resource "aws_apigatewayv2_route" "unauthenticated" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.unauthenticated.id}"
  route_key      = "GET /unauthenticated_root_function"
  operation_name = "my_operation"
  depends_on = [aws_apigatewayv2_integration.unauthenticated]
}

resource "aws_apigatewayv2_integration" "unauthenticated" {
  api_id                 = aws_apigatewayv2_api.root_http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.function1.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "auth_root_integration" {
  api_id                 = aws_apigatewayv2_api.root_http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.authorized_function1.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "header_root_function_resource_get_route" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.auth_root_integration.id}"
  route_key      = "GET /header_root_function"
  operation_name = "my_operation"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.root_header_authorizer.id
  depends_on = [aws_apigatewayv2_integration.unauthenticated]
}

resource "aws_apigatewayv2_authorizer" "root_header_authorizer" {
  api_id           = aws_apigatewayv2_api.root_http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = aws_lambda_function.authorizer1.invoke_arn
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader"]
  name             = "header_authorizer"
}

resource "aws_apigatewayv2_route" "get_hello_request" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.auth_root_integration.id}"
  route_key      = "GET /request_root_function"
  operation_name = "header_root_function"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.root_request_authorizer.id
}

resource "aws_apigatewayv2_authorizer" "root_request_authorizer" {
  api_id           = aws_apigatewayv2_api.root_http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = aws_lambda_function.authorizer1.invoke_arn
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader", "$request.querystring.mystring"]
  name             = "request_authorizer"
}

resource "aws_apigatewayv2_route" "unauthenticated_module_function" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.function2.id}"
  route_key      = "GET /unauthenticated_module_function"
  operation_name = "header_root_function"
}

resource "aws_apigatewayv2_integration" "function2" {
  api_id                 = aws_apigatewayv2_api.root_http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = module.function2.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_authorizer" "module_header_authorizer" {
  api_id           = aws_apigatewayv2_api.root_http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = module.function2.authorizer_invoke_arn
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader"]
  name             = "module_header_authorizer"
}

resource "aws_apigatewayv2_route" "module_header_function" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.module_authorizer_integration.id}"
  route_key      = "GET /header_module_function"
  operation_name = "module_header_function"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.module_header_authorizer.id
}

resource "aws_apigatewayv2_authorizer" "module_request_authorizer" {
  api_id           = aws_apigatewayv2_api.root_http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = module.function2.authorizer_invoke_arn
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader", "$request.querystring.mystring"]
  name             = "module_request_authorizer"
}

resource "aws_apigatewayv2_route" "module_request_function" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.module_authorizer_integration.id}"
  route_key      = "GET /request_module_function"
  operation_name = "module_header_function"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.module_request_authorizer.id
}

resource "aws_apigatewayv2_integration" "module_authorizer_integration" {
  api_id                 = aws_apigatewayv2_api.root_http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = module.function2.authorized_function_invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "serverless_function_route" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.serverless_function_resource_integration.id}"
  route_key      = "GET /unauthenticated_serverless_function"
  operation_name = "serverless_function_route"
}

resource "aws_apigatewayv2_integration" "serverless_function_resource_integration" {
  api_id                 = aws_apigatewayv2_api.root_http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = module.function7.lambda_function_invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "serverless_function_resource_auth_integration" {
  api_id                 = aws_apigatewayv2_api.root_http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = module.authorized_function7.lambda_function_invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "serverless_header_route" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.serverless_function_resource_auth_integration.id}"
  route_key      = "GET /header_serverless_function"
  operation_name = "serverless_function_route"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.serverless_header_authorizer.id
}

resource "aws_apigatewayv2_authorizer" "serverless_header_authorizer" {
  api_id           = aws_apigatewayv2_api.root_http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = module.authorizer7.lambda_function_invoke_arn
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader"]
  name             = "serverless_header_authorizer"
}

resource "aws_apigatewayv2_route" "serverless_request_route" {
  api_id         = aws_apigatewayv2_api.root_http_api.id
  target         = "integrations/${aws_apigatewayv2_integration.serverless_function_resource_auth_integration.id}"
  route_key      = "GET /request_serverless_function"
  operation_name = "serverless_request_route"
  authorization_type = "CUSTOM"
  authorizer_id = aws_apigatewayv2_authorizer.serverless_request_authorizer.id
}

resource "aws_apigatewayv2_authorizer" "serverless_request_authorizer" {
  api_id           = aws_apigatewayv2_api.root_http_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = module.authorizer7.lambda_function_invoke_arn
  authorizer_credentials_arn = aws_iam_role.invocation_role.arn
  authorizer_payload_format_version = "2.0"
  identity_sources = ["$request.header.myheader", "$request.querystring.mystring"]
  name             = "serverless_request_authorizer"
}

module "module_rest_api" {
  source = "./v2_api"
  unauthenticated_function = module.function7.lambda_function_invoke_arn
  authenticated_function = module.authorized_function7.lambda_function_invoke_arn
  autherizer_function = module.authorizer7.lambda_function_invoke_arn
  rest_api_name = "module_http_api"
}

#
#resource "aws_api_gateway_deployment" "root_rest_api_deployment" {
#  rest_api_id = aws_api_gateway_rest_api.root_rest_api.id
#
#  depends_on = [
#    aws_api_gateway_integration.header_root_function_resource_integration,
#    aws_api_gateway_integration.header_serverless_function_resource_integration,
#    aws_api_gateway_integration.module_function_resource_integration,
#    aws_api_gateway_integration.request_module_function_resource_integration,
#    aws_api_gateway_integration.request_root_function_resource_integration,
#    aws_api_gateway_integration.request_serverless_function_resource_integration,
#    aws_api_gateway_integration.root_function_resource_integration,
#    aws_api_gateway_integration.serverless_function_resource_integration,
#  ]
#}

