variable "instance_type" {
    default = "t2.micro"
}
variable "key_name" {
    default = "my_aws_key"
}
variable "AMI_ID" {
    default = "ami-0e35ddab05955cf57"
}
variable "security_groups" {}
variable "environment" {}
variable "aws_region" {
    default = "ap-south-1"
}

