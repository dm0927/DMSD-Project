CREATE TABLE SERVICE( 
            Service_ID int, 
            Vehicle_type varchar(25), 
            Labor varchar(25), 
            Price float,
            Skill_ID int,
            primary key(Service_ID,Vehicle_type),
            foreign key (Skill_ID) references Skill(SKill_ID),
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );