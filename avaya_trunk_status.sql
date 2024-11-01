/*
SQLyog Community v13.1.7 (64 bit)
MySQL - 10.3.27-MariaDB : Database - Monitor
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`Monitor` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `Monitor`;

/*Table structure for table `Trunks` */

DROP TABLE IF EXISTS `Trunks`;

CREATE TABLE `Trunks` (
  `trunk_no` char(3) NOT NULL,
  `in_use` int(3) NOT NULL,
  `idle` int(3) NOT NULL,
  `oos` int(3) NOT NULL,
  `updated` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  UNIQUE KEY `trunk_no` (`trunk_no`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `Trunks` */

insert  into `Trunks`(`trunk_no`,`in_use`,`idle`,`oos`,`updated`) values 
('21',32,223,0,'2021-03-01 11:02:12'),
('22',90,165,0,'2021-03-01 11:02:13'),
('23',0,255,0,'2021-03-01 11:02:14'),
('24',155,100,0,'2021-03-01 11:02:15');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
