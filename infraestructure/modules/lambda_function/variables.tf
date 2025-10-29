variable "function_name" {
  type = string
}

variable "image_uri" {
  type = string
}

variable "telegram_bot_token" {
  type      = string
  sensitive = true
}

variable "gemini_api_key" {
  type      = string
  sensitive = true
}

variable "google_sheet_id" {
  type = string
}

variable "google_credentials_json" {
  type      = string
  sensitive = true
  description = "Base64-encoded JSON of Google Service Account credentials"
}
