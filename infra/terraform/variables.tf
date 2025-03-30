variable "key_name" {
    default = my_aws_key

  
}
variable "aws_region" {
    default = ap-south-1
  
}

variable "instance_type" {
    default = t2.micro
  
}

variable "evnironment" {
    description = "Prod or DEV"
    type = string
  
}

variable "AMI_ID" {
    default = ami-0e35ddab05955cf57
  
}