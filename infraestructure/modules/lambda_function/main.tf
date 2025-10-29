provider "aws" {
  region = "sa-east-1"
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  package_type  = "Image"
  image_uri     = var.image_uri
  role          = aws_iam_role.lambda_role.arn
  timeout       = 15

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN  = var.telegram_bot_token
      GEMINI_API_KEY      = var.gemini_api_key
      GOOGLE_SHEET_ID     = var.google_sheet_id
      GOOGLE_CREDENTIALS_JSON_BASE64 = var.google_credentials_json
    }
  }
}

resource "aws_lambda_function_url" "url" {
  function_name      = aws_lambda_function.this.function_name
  authorization_type = "NONE"
}