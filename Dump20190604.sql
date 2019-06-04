-- MySQL dump 10.13  Distrib 5.7.16, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: mmp
-- ------------------------------------------------------
-- Server version	5.7.16-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `class` (
  `cnum` int(11) NOT NULL AUTO_INCREMENT,
  `cname` varchar(45) NOT NULL,
  `ccontent` varchar(100) DEFAULT NULL,
  `ctime` datetime DEFAULT NULL,
  `cmax` int(11) DEFAULT NULL,
  PRIMARY KEY (`cnum`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class`
--

LOCK TABLES `class` WRITE;
/*!40000 ALTER TABLE `class` DISABLE KEYS */;
INSERT INTO `class` VALUES (1,'PT','test','2019-06-01 13:00:00',6),(2,'PT','test','2019-06-01 13:00:00',6),(3,'PT','test','2019-06-12 13:00:00',6),(4,'요가','test','2019-06-13 13:00:00',6),(5,'복','test','2019-06-14 13:00:00',6),(6,'줄넘','test','2019-06-15 13:00:00',6),(7,'pt','test','2019-05-31 13:00:00',6),(8,'줄넘기','test','2019-06-01 13:00:00',6),(9,'pt','test','2019-06-04 13:00:00',3),(10,'줄넘기 ','유산소 운동 입니다','2019-06-05 13:00:00',6),(11,'pt ','개별 코치 하는 강의 입니다','2019-06-05 13:00:00',3),(12,'요가','유연성 증가 ','2019-06-05 13:00:00',8),(13,'필라테스 ','근력운','2019-06-05 13:00:00',6);
/*!40000 ALTER TABLE `class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member`
--

DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `member` (
  `mnum` int(11) NOT NULL AUTO_INCREMENT,
  `mname` varchar(45) NOT NULL,
  `mphone` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`mnum`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member`
--

LOCK TABLES `member` WRITE;
/*!40000 ALTER TABLE `member` DISABLE KEYS */;
INSERT INTO `member` VALUES (1,'이지은','8016'),(2,'이정은','1234'),(3,'회원1','123'),(4,'회원2','1231'),(5,'회원3','123123'),(6,'회원4','123'),(7,'회원5','123');
/*!40000 ALTER TABLE `member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sugan`
--

DROP TABLE IF EXISTS `sugan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sugan` (
  `snum` int(11) NOT NULL AUTO_INCREMENT,
  `mnum` int(11) NOT NULL,
  `cnum` int(11) DEFAULT NULL,
  PRIMARY KEY (`snum`),
  KEY `mnum_idx` (`mnum`),
  KEY `cnum_idx` (`cnum`),
  CONSTRAINT `cnum` FOREIGN KEY (`cnum`) REFERENCES `class` (`cnum`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `mnum` FOREIGN KEY (`mnum`) REFERENCES `member` (`mnum`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sugan`
--

LOCK TABLES `sugan` WRITE;
/*!40000 ALTER TABLE `sugan` DISABLE KEYS */;
INSERT INTO `sugan` VALUES (2,2,2),(3,1,3),(4,2,3),(5,1,4),(6,1,5),(10,2,8),(42,3,8),(43,4,8),(44,5,8),(45,6,8),(81,7,8),(85,1,2),(86,1,1),(90,1,10),(93,1,12),(94,1,9);
/*!40000 ALTER TABLE `sugan` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-06-04 11:30:57
