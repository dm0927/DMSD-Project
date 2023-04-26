CREATE TABLE BILLPART(
            Appoint_ID int, 
            Part_ID int, 
            Invoice_ID int,
            Price float,
            primary key(Appoint_ID,Part_ID,Invoice_ID), 
            foreign key (Appoint_ID) references Appointment(Appoint_ID),
            foreign key (Part_ID) references Part(Part_ID),
            foreign key (Invoice_ID) references Invoice(Invoice_ID),
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );