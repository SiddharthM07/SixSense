variable "instance_type" {
    default = "t2.micro"
}
variable "key_name" {
    default = "aws-key"
}
variable "AMI_ID" {
    default = "ami-xxx"
}
variable "security_groups" {}
variable "environment" {}
variable "aws_region" {
    default = "enter-region"
}

