terraform {
  source = "../../modules/lambda_function"
}

inputs = {
  function_name = "asistente-gastos"
  image_uri     = "<AMAZONID>.dkr.ecr.sa-east-1.amazonaws.com/asistente-gastos:latest"
}
