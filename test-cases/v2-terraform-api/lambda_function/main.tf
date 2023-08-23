variable "source_code" {
  type = string
}

variable "function_name" {
  type = string
}

variable "authorized_function_name" {
  type = string
}

variable "authorizer_function_name" {
  type = string
}

variable "AuthHandler" {
  type    = string
}

variable "layers" {
  type = list
  default = []
}

resource "random_uuid" "unique_id" {
    keepers = {
        my_key = "my_key"
    }
}


resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda2_${random_uuid.unique_id.result}"

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

resource "aws_lambda_function" "this" {
    filename = var.source_code
    handler = "app.unauthenticated_lambda_handler"
    runtime = "python3.8"
    function_name = var.function_name
    role = aws_iam_role.iam_for_lambda.arn
    layers = var.layers
    timeout = 300
}

resource "aws_lambda_function" "authorized_this" {
    filename = var.source_code
    handler = "app.lambda_handler"
    runtime = "python3.8"
    function_name = var.authorized_function_name
    role = aws_iam_role.iam_for_lambda.arn
    layers = var.layers
    timeout = 300
}

resource "aws_lambda_function" "authorizer" {
    filename = var.source_code
    handler = var.AuthHandler
    runtime = "python3.8"
    function_name = var.authorizer_function_name
    role = aws_iam_role.iam_for_lambda.arn
    layers = var.layers
    timeout = 300
}

output "arn" {
  value = aws_lambda_function.this.arn
}

output "invoke_arn" {
  value = aws_lambda_function.this.invoke_arn
}


output "authorized_function_arn" {
  value = aws_lambda_function.authorized_this.arn
}

output "authorized_function_invoke_arn" {
  value = aws_lambda_function.authorized_this.invoke_arn
}

output "authorizer_arn" {
  value = aws_lambda_function.authorizer.arn
}

output "authorizer_invoke_arn" {
  value = aws_lambda_function.authorizer.invoke_arn
}