const express = require('express')
const app = express()
	
const sqlite3 = require('sqlite3').verbose();
var database = new sqlite3.Database(
    './database.sqlite3', 
    (err) => {
        if (err)
            return console.error(err.message);
    });

// database.run(
//     `INSERT INTO Schedule(
//         TableNumber,
//         Name,
//         PhoneNumber,
//         Email,
//         Datetime,
//         TimeStart,
//         TimeEnd)
//         VALUES
//             (1, '', '', '', '', '', '')`);

// database.each(
//     `SELECT * FROM Schedule`,
//     [],
//     (err, row) => {console.log(row)});

// database.run("DROP TABLE Schedule")

// database.run(
//     `CREATE TABLE Schedule(
//         ScheduleEntryID INTEGER PRIMARY KEY AUTOINCREMENT,
//         TableNumber INTEGER,
//         Name TEXT,
//         PhoneNumber TEXT,
//         Email TEXT,
//         Datetime TEXT,
//         TimeStart TEXT,
//         TimeEnd TEXT)`);

function getDates() {
    var dates = [];
    var datetime = new Date().getTime();

    for(var i = 0; i < 7; i++) {
        dates.push(new Date(datetime).toLocaleDateString());
        
        datetime += 24 * 60 * 60 * 1000;
    }

    return dates;
}

function addScheduleEntry(
        table_number, 
        name, 
        phone_number, 
        email, 
        datetime,
        time_start,
        time_end) {
    database.run(
        `INSERT INTO Schedule(
            TableNumber,
            Name,
            PhoneNumber,
            Email,
            Datetime,
            TimeStart,
            TimeEnd)
            VALUES  (?, ?, ?, ?, ?, ?, ?)`,
        [table_number, 
         name, 
         phone_number, 
         email, 
         datetime,
         time_start,
         time_end]);
}

app.set("view engine", "hbs");

app.use(express.static('public'))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

app.get(
    '/', 
    (req, res) => res.redirect("/index.html"))

app.use(
    '/index.html',
    (req, res) => {
        let access_str = "";
        let reservation_str = "";

        if (req.method == "POST" 
                & req.body.query_type == "access")
            if (req.body.time_start >= req.body.time_end) {
                access_str = 
                    "Время было указанно некорректно. Время начала было больше либо равно времени конца.";

                res.render(
                    'index.hbs',
                    { 
                        select_time: 
                            ['12:00', '13:00', '14:00', '15:00', '16:00', 
                                '17:00', '18:00', '19:00', '20:00', '21:00'],
                        tables: [1, 2, 3, 4, 5, 6],
                        dates: getDates(),
                        access_result: access_str,
                        reservation_result: reservation_str
                    });
            }
            
            else {
                function renderAccessMessage(err, rows) {
                    let table_is_accessible = true;

                    for (let i = 0; i < rows.length; i++)
                        if (rows[i].TimeEnd 
                                > req.body.time_start
                                & rows[i].TimeStart 
                                < req.body.time_end)
                            table_is_accessible = false;

                    if (!table_is_accessible)
                        access_str = 
                            "Столик номер " 
                            + req.body.table
                            + " уже забронирован " 
                            + req.body.date 
                            + " числа между " 
                            + req.body.time_start
                            + " и " + req.body.time_end;
                    else
                        access_str = 
                            "Столик номер " 
                            + req.body.table
                            + " свободен для бронирования " 
                            + req.body.date 
                            + " числа между " 
                            + req.body.time_start 
                            + " и " 
                            + req.body.time_end;

                    res.render(
                        'index.hbs',
                        { 
                            select_time: 
                                ['12:00', 
                                 '13:00', 
                                 '14:00', 
                                 '15:00', 
                                 '16:00', 
                                 '17:00', 
                                 '18:00', 
                                 '19:00',  
                                 '20:00', 
                                 '21:00'],
                            tables: [1, 2, 3, 4, 5, 6],
                            dates: getDates(),
                            access_result: access_str,
                            reservation_result: reservation_str
                        });
                }

                database.all(
                    `SELECT * FROM Schedule
                        WHERE TableNumber = ? 
                            AND Datetime = ?`,
                    [parseInt(req.body.table), req.body.date],
                    renderAccessMessage);
            }
        else if (req.method == "POST" 
                & req.body.query_type == "reservation")
            if (!req.body.hasOwnProperty("table1")
                    & !req.body.hasOwnProperty("table2")
                    & !req.body.hasOwnProperty("table3")
                    & !req.body.hasOwnProperty("table4")
                    & !req.body.hasOwnProperty("table5")
                    & !req.body.hasOwnProperty("table6")) {
                reservation_str = "Ни один стол не был выбран";

                res.render(
                    'index.hbs',
                    { 
                        select_time: 
                            ['12:00', '13:00', '14:00', '15:00', '16:00', 
                                '17:00', '18:00', '19:00', '20:00', '21:00'],
                        tables: [1, 2, 3, 4, 5, 6],
                        dates: getDates(),
                        access_result: access_str,
                        reservation_result: reservation_str
                    });
            }
            
            else if (req.body.time_start >= req.body.time_end) {
                reservation_str = 
                    "Время было указанно некорректно. Время начала было больше либо равно времени конца.";

                res.render(
                    'index.hbs',
                    { 
                        select_time: 
                            ['12:00', '13:00', '14:00', '15:00', '16:00', 
                                '17:00', '18:00', '19:00', '20:00', '21:00'],
                        tables: [1, 2, 3, 4, 5, 6],
                        dates: getDates(),
                        access_result: access_str,
                        reservation_result: reservation_str
                    });
            }
            
            else {
                let tables_numbers = [];
                let tables_names = 
                    ["table1", 
                     "table2", 
                     "table3",
                     "table4", 
                     "table5", 
                     "table6"];
                let tablesDisjunction = "(TableNumber = ?";
                
                for (let table_name of tables_names)
                    if (req.body.hasOwnProperty(table_name)) {
                        tables_numbers.push(
                            parseInt(table_name[5]));

                        if (tables_numbers.length > 1)
                            tablesDisjunction += 
                                " OR TableNumber = ?";
                    }

                tablesDisjunction += ")";

                function renderReservationMessage(err, rows) {
                    let tables_are_accessible = true;
                    
                    for (let i = 0; i < rows.length; i++)
                        if (rows[i].TimeEnd 
                                > req.body.time_start
                                & rows[i].TimeStart 
                                < req.body.time_end)
                            tables_are_accessible = false;
                    
                    if (!tables_are_accessible)
                        reservation_str =
                            "Стол(ы) " 
                            + tables_numbers.toString()
                            + " уже забронированы " 
                            + req.body.date 
                            + " числа между " 
                            + req.body.time_start
                            + " и " + req.body.time_end;
                    else {
                        for (
                                let i = 0; 
                                i < tables_numbers.length; 
                                i++)
                            addScheduleEntry(
                                tables_numbers[i],
                                req.body.name, 
                                req.body.phone,
                                req.body.email,
                                req.body.date,
                                req.body.time_start,
                                req.body.time_end);

                        reservation_str =
                            "Стол(ы) " 
                            + tables_numbers.toString()
                            + " были успешно забронированы на " 
                            + req.body.date 
                            + " число между " 
                            + req.body.time_start 
                            + " и " 
                            + req.body.time_end;
                    }

                    res.render(
                        'index.hbs',
                        { 
                            select_time: 
                                ['12:00', 
                                 '13:00', 
                                 '14:00', 
                                 '15:00', 
                                 '16:00', 
                                 '17:00', 
                                 '18:00', 
                                 '19:00',  
                                 '20:00', 
                                 '21:00'],
                            tables: [1, 2, 3, 4, 5, 6],
                            dates: getDates(),
                            access_result: access_str,
                            reservation_result: reservation_str
                        });
                }
                
                database.all(
                    "SELECT * FROM Schedule "
                        + "WHERE " 
                            + tablesDisjunction
                            + "AND Datetime = ?",
                    tables_numbers.concat([req.body.date]),
                    renderReservationMessage);
            }
        else
            res.render(
                'index.hbs',
                { 
                    select_time: 
                        ['12:00', '13:00', '14:00', '15:00',
                         '16:00', '17:00', '18:00', '19:00', 
                         '20:00', '21:00'],
                    tables: [1, 2, 3, 4, 5, 6],
                    dates: getDates(),
                    access_result: access_str,
                    reservation_result: reservation_str
                });
    })

app.listen(3000)