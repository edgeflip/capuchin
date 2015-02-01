provider "aws" {
    access_key = "${var.access_key}"
    secret_key = "${var.secret_key}"
    region = "${var.region}"
}

resource "aws_instance" "capuchin" {
    ami = "${lookup(var.amis, var.region)}"
    instance_type = "t1.micro"

    provisioner "docker" {
        inline = [
            "sudo apt-get update",
            "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9",
            "sudo sh -c \"echo deb https://get.docker.com/ubuntu docker main /etc/apt/sources.list.d/docker.list\"",
            "sudo apt-get update",
            "sudo apt-get install lxc-docker",
            "sudo apt-get install git",
            "git clone ${var.git_repo}"
            "sudo pip install fig"
            "cd ${var.app}",
            "sudo fig up"
        ]
    }
}

resource "aws_eip" "ip"{
    instance = "${aws_instance.capuchin.id}"
}

output "ip" {
    value = "${aws_eip.ip.public_ip}"
}
