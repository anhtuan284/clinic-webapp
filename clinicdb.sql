-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: clinicdb
-- ------------------------------------------------------
-- Server version	8.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id` int NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appointment`
--

DROP TABLE IF EXISTS `appointment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `scheduled_date` date DEFAULT NULL,
  `scheduled_hour` time DEFAULT NULL,
  `is_confirm` tinyint(1) DEFAULT NULL,
  `is_paid` tinyint(1) DEFAULT NULL,
  `status` tinyint(1) DEFAULT NULL,
  `appointment_list_id` int DEFAULT NULL,
  `patient_id` int NOT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `appointment_list_id` (`appointment_list_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`appointment_list_id`) REFERENCES `appointment_list` (`id`),
  CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
INSERT INTO `appointment` VALUES (1,'2024-04-30','15:30:00',0,0,1,1,2,'2024-05-04 17:19:45','2024-05-04 17:19:45'),(2,'2024-04-30','16:30:00',0,0,1,1,2,'2024-05-04 17:19:45','2024-05-04 17:19:45'),(3,'2024-04-30','08:30:00',0,0,1,1,2,'2024-05-04 17:19:45','2024-05-04 17:19:45'),(4,'2024-04-30','09:30:00',0,0,1,1,2,'2024-05-04 17:19:45','2024-05-04 17:19:45'),(5,'2024-04-30','11:30:00',0,0,1,1,2,'2024-05-04 17:19:45','2024-05-04 17:19:45');
/*!40000 ALTER TABLE `appointment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appointment_list`
--

DROP TABLE IF EXISTS `appointment_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointment_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `scheduled_date` date DEFAULT NULL,
  `nurse_id` int NOT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `scheduled_date` (`scheduled_date`),
  KEY `nurse_id` (`nurse_id`),
  CONSTRAINT `appointment_list_ibfk_1` FOREIGN KEY (`nurse_id`) REFERENCES `nurse` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment_list`
--

LOCK TABLES `appointment_list` WRITE;
/*!40000 ALTER TABLE `appointment_list` DISABLE KEYS */;
INSERT INTO `appointment_list` VALUES (1,'2024-04-30',5,'2024-05-04 17:15:35','2024-05-04 17:15:35'),(2,'2024-04-25',5,'2024-05-04 17:15:55','2024-05-04 17:15:55');
/*!40000 ALTER TABLE `appointment_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bill`
--

DROP TABLE IF EXISTS `bill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bill` (
  `service_price` decimal(10,2) DEFAULT NULL,
  `medicine_price` decimal(10,2) DEFAULT NULL,
  `total` decimal(11,2) DEFAULT NULL,
  `prescription_id` int NOT NULL,
  `cashier_id` int DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  PRIMARY KEY (`prescription_id`),
  KEY `cashier_id` (`cashier_id`),
  CONSTRAINT `bill_ibfk_1` FOREIGN KEY (`prescription_id`) REFERENCES `prescription` (`id`),
  CONSTRAINT `bill_ibfk_2` FOREIGN KEY (`cashier_id`) REFERENCES `cashier` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bill`
--

LOCK TABLES `bill` WRITE;
/*!40000 ALTER TABLE `bill` DISABLE KEYS */;
/*!40000 ALTER TABLE `bill` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cashier`
--

DROP TABLE IF EXISTS `cashier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cashier` (
  `id` int NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `cashier_ibfk_1` FOREIGN KEY (`id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cashier`
--

LOCK TABLES `cashier` WRITE;
/*!40000 ALTER TABLE `cashier` DISABLE KEYS */;
INSERT INTO `cashier` VALUES (1);
/*!40000 ALTER TABLE `cashier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (1,'Thuốc Giảm Đau','2024-05-04 16:53:10','2024-05-04 16:53:10'),(2,'Thuốc Ho','2024-05-04 16:53:10','2024-05-04 16:53:10'),(3,'Thuốc Cảm','2024-05-04 16:53:10','2024-05-04 16:53:10'),(4,'Thực Phẩm Chức Năng','2024-05-04 17:01:03','2024-05-04 17:01:03');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctor`
--

DROP TABLE IF EXISTS `doctor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor` (
  `id` int NOT NULL,
  `year_exp` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `doctor_ibfk_1` FOREIGN KEY (`id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor`
--

LOCK TABLES `doctor` WRITE;
/*!40000 ALTER TABLE `doctor` DISABLE KEYS */;
INSERT INTO `doctor` VALUES (4,13);
/*!40000 ALTER TABLE `doctor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicine`
--

DROP TABLE IF EXISTS `medicine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicine` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `usage` varchar(50) DEFAULT NULL,
  `exp` date DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicine`
--

LOCK TABLES `medicine` WRITE;
/*!40000 ALTER TABLE `medicine` DISABLE KEYS */;
INSERT INTO `medicine` VALUES (1,'Panadol',10000.00,'Uống sau bữa ăn','2025-12-31','2024-05-04 16:54:32','2024-05-04 16:54:32'),(2,'Zinc',20000.00,'Uống trước khi ngủ','2024-06-30','2024-05-04 16:54:32','2024-05-04 16:54:32'),(3,'Vitamin C',30000.00,'Uống trước khi ngủ','2024-06-30','2024-05-04 16:54:32','2024-05-04 16:54:32');
/*!40000 ALTER TABLE `medicine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicine_category`
--

DROP TABLE IF EXISTS `medicine_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicine_category` (
  `category_id` int NOT NULL,
  `medicine_id` int NOT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  PRIMARY KEY (`category_id`,`medicine_id`),
  KEY `medicine_id` (`medicine_id`),
  CONSTRAINT `medicine_category_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`),
  CONSTRAINT `medicine_category_ibfk_2` FOREIGN KEY (`medicine_id`) REFERENCES `medicine` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicine_category`
--

LOCK TABLES `medicine_category` WRITE;
/*!40000 ALTER TABLE `medicine_category` DISABLE KEYS */;
INSERT INTO `medicine_category` VALUES (1,1,'2024-05-04 17:02:10','2024-05-04 17:02:10'),(3,1,'2024-05-04 17:02:10','2024-05-04 17:02:10'),(4,2,'2024-05-04 17:02:10','2024-05-04 17:02:10'),(4,3,'2024-05-04 17:02:10','2024-05-04 17:02:10');
/*!40000 ALTER TABLE `medicine_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicine_detail`
--

DROP TABLE IF EXISTS `medicine_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicine_detail` (
  `quantity` int DEFAULT NULL,
  `usage` varchar(100) DEFAULT NULL,
  `prescription_id` int NOT NULL,
  `medicine_id` int NOT NULL,
  `medicine_unit_id` int DEFAULT NULL,
  PRIMARY KEY (`prescription_id`,`medicine_id`),
  KEY `medicine_id` (`medicine_id`),
  KEY `medicine_unit_id` (`medicine_unit_id`),
  CONSTRAINT `medicine_detail_ibfk_1` FOREIGN KEY (`prescription_id`) REFERENCES `prescription` (`id`),
  CONSTRAINT `medicine_detail_ibfk_2` FOREIGN KEY (`medicine_id`) REFERENCES `medicine` (`id`),
  CONSTRAINT `medicine_detail_ibfk_3` FOREIGN KEY (`medicine_unit_id`) REFERENCES `medicine_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicine_detail`
--

LOCK TABLES `medicine_detail` WRITE;
/*!40000 ALTER TABLE `medicine_detail` DISABLE KEYS */;
INSERT INTO `medicine_detail` VALUES (2,'2 lần/ngày, sáng chiều',1,1,1),(1,'2 lần/ngày, sáng chiều',1,2,2),(2,'2 lần/ngày, sáng chiều',1,3,1);
/*!40000 ALTER TABLE `medicine_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicine_unit`
--

DROP TABLE IF EXISTS `medicine_unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicine_unit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `unit_id` int DEFAULT NULL,
  `medicine_id` int DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `unit_id` (`unit_id`),
  KEY `medicine_id` (`medicine_id`),
  CONSTRAINT `medicine_unit_ibfk_1` FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`),
  CONSTRAINT `medicine_unit_ibfk_2` FOREIGN KEY (`medicine_id`) REFERENCES `medicine` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicine_unit`
--

LOCK TABLES `medicine_unit` WRITE;
/*!40000 ALTER TABLE `medicine_unit` DISABLE KEYS */;
INSERT INTO `medicine_unit` VALUES (1,1,3,14),(2,1,2,8),(3,2,2,30),(4,1,1,10),(5,3,1,1);
/*!40000 ALTER TABLE `medicine_unit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nurse`
--

DROP TABLE IF EXISTS `nurse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nurse` (
  `id` int NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `nurse_ibfk_1` FOREIGN KEY (`id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nurse`
--

LOCK TABLES `nurse` WRITE;
/*!40000 ALTER TABLE `nurse` DISABLE KEYS */;
INSERT INTO `nurse` VALUES (5);
/*!40000 ALTER TABLE `nurse` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient`
--

DROP TABLE IF EXISTS `patient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient` (
  `id` int NOT NULL,
  `height` int DEFAULT NULL,
  `weight` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `patient_ibfk_1` FOREIGN KEY (`id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (2,156,55),(3,156,55);
/*!40000 ALTER TABLE `patient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policy`
--

DROP TABLE IF EXISTS `policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policy` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `value` varchar(100) NOT NULL,
  `admin_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `policy_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policy`
--

LOCK TABLES `policy` WRITE;
/*!40000 ALTER TABLE `policy` DISABLE KEYS */;
/*!40000 ALTER TABLE `policy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prescription`
--

DROP TABLE IF EXISTS `prescription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `symptoms` varchar(1000) DEFAULT NULL,
  `diagnosis` varchar(1000) DEFAULT NULL,
  `doctor_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `appointment_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `patient_id` (`patient_id`),
  KEY `appointment_id` (`appointment_id`),
  CONSTRAINT `prescription_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`),
  CONSTRAINT `prescription_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`),
  CONSTRAINT `prescription_ibfk_3` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prescription`
--

LOCK TABLES `prescription` WRITE;
/*!40000 ALTER TABLE `prescription` DISABLE KEYS */;
INSERT INTO `prescription` VALUES (1,'2024-04-30','Ho sổ mũi nhiều đờm','Cảm cúm',4,2,1),(2,'2024-04-30','Ho sổ mũi nhiều đờm','Cảm cúm',4,2,2);
/*!40000 ALTER TABLE `prescription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unit`
--

DROP TABLE IF EXISTS `unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unit`
--

LOCK TABLES `unit` WRITE;
/*!40000 ALTER TABLE `unit` DISABLE KEYS */;
INSERT INTO `unit` VALUES (1,'vỉ'),(2,'chai'),(3,'viên');
/*!40000 ALTER TABLE `unit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(120) NOT NULL,
  `role` enum('ADMIN','PATIENT','DOCTOR','NURSE','CASHIER') NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `cid` varchar(12) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `phone` varchar(14) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `gender` enum('MALE','FEMALE') DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `avatar` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `ix_user_cid` (`cid`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'cashier','$2b$12$VAns3fPqjmO3jySnmheQxepQgiVGENYwBabQo9/oDjrzoQzdvPqMu','CASHIER','Thao Van','6854651894','2024-05-04','0123456789','cashier@example.com','FEMALE','Clinic','https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg'),(2,'patient2','$2b$12$yeQjIwL7bo13FGlsqYrLNu0tQ6VuJoYFkn655IrMs2yc7j2Hrq0hG','PATIENT','Quốc Tuấn','2654894321','2024-05-04','0123456789','patient2@example.com','MALE','Clinic','https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg'),(3,'patient3','$2b$12$62Hd0Vo6/EgTaqk6e4v79umWi0kdqBTDLma90OyML.r/q.uR1w4Vu','PATIENT','Anh Tuấn','32589441528','2024-05-04','0123456789','patient3@example.com','MALE','Clinic','https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg'),(4,'doctorstrange','$2b$12$.cauqiGOC4WFGgY/M6JHMuB2gYetLA7HQM47tchFsBoU7prR3qGoO','DOCTOR','Doctor Strange','092884828872','2024-05-04','0123456789','docter@example.com','MALE','Clinic','https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg'),(5,'nurse','$2b$12$L5zjoaYkgv9ZaVZdamTdeO49XByLwpMVJWOkJECAgrt26K3jWJrqq','NURSE','Luu Danh','23498423189','2024-05-04','0123456789','cashier123@example.com','MALE','Clinic','https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-05-04 18:39:41
