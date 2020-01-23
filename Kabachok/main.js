const express = require('express')
const app = express()
	
const sqlite3 = require('sqlite3').verbose();
let database = new sqlite3.Database(
    ':memory:', 
    (err) => {
        if (err)
            return console.error(err.message);
    });



function getDates() {
    var dates = [];
    var datetime = new Date().getTime();

    for(var i = 0; i < 7; i++) {
        dates.push(new Date(datetime).toLocaleDateString());
        
        datetime += 24 * 60 * 60 * 1000;
    }

    return dates;
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
        // console.log(req.body)
        res.render(
            'index.hbs',
            { 
                select_time: 
                    ['12:00', '13:00', '14:00', '15:00', '16:00', 
                     '17:00', '18:00', '19:00', '20:00', '21:00'],
                tables: [1, 2, 3, 4, 5, 6],
                dates: getDates(),
                // access_result: "321",
                // reservation_result: "123"
            });
    })

app.listen(3000)