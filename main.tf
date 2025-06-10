terraform {
  backend "s3" {
    bucket         = "terraform-state-wilczg"       # dokładnie jak utworzyłeś
    key            = "lambda/terraform.tfstate"     # ścieżka w bucketcie
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

resource "aws_sns_topic" "alerts" {
  name = "TemperatureAlerts"
}

resource "aws_lambda_function" "temperature_processor" {
  function_name = "temperatureProcessor"
  runtime       = "python3.12"
  handler       = "lambda_function.lambda_handler"
  filename      = "./lambda_function.zip"
  timeout       = 10
  memory_size   = 128
  role          = "arn:aws:iam::136590348108:role/LabRole"
}

data "archive_file" "lambda_package" {
  type        = "zip"
  source_file = "${path.module}/lambda/lambda_function.py"
  output_path = "${path.module}/lambda_function_payload.zip"
}