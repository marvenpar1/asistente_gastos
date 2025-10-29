output "function_url" {
  value       = aws_lambda_function_url.url.function_url
  description = "Public URL for invoking the Lambda function"
}
