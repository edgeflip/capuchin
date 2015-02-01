variable "access_key" {}
variable "secret_key" {}
variable "region" {
    default = "us-east-1"
}
variable "amis" {
    default = {
        us-east-1 = "ami-86562dee"
        us-west-1 = "ami-50120b15"
    }
}

variable "git_repo" {}
variable "app" {}
variable "key_path" {}
