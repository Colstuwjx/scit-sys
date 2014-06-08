CREATE DATABASE IF NOT EXISTS scit default charset utf8 COLLATE utf8_general_ci;

use scit;
CREATE TABLE scit_vm(
    vm_id int unsigned not null auto_increment,
    vm_name varchar(20) not null unique,
    vm_fixip char(16),
    vm_floatip char(16),
    vm_create_time timestamp default CURRENT_TIMESTAMP,
    vm_status char(16),
    PRIMARY KEY(vm_id)
) default charset=utf8 auto_increment=1;
