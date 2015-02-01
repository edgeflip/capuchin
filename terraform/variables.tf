variable "access_key" {}
variable "secret_key" {}
variable "region" {
    default = "us-east-1"
}
variable "amis" {
    default = {
        us-east-1 = "ami-408c7f28"
        us-west-2 = "ami-3bebb50b"
    }
}

variable "git_repo" {}
variable "app" {}
