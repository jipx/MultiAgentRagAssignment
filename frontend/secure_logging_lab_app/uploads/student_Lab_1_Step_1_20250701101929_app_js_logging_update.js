/// ORIGINAL VS MODIFIED app.js SIDE-BY-SIDE COMPARISON

// --- Original app.js ---                                 // --- Modified app.js ---

var express = require('express');                          var express = require('express');
var bodyParser = require('body-parser');                  var bodyParser = require('body-parser');
var app = express();                                      var app = express();
var user = require('../model/user.js');                   var user = require('../model/user.js');
var cors = require('cors');                               var cors = require('cors');
var validator = require('validator');                     var validator = require('validator');
//var validateFn=require('../validation/validationFns');   var fs = require('fs');
                                                         var path = require('path');
                                                         var morgan = require('morgan');
                                                         var rfs = require('rotating-file-stream');

app.options('*', cors());                                 app.options('*', cors());
app.use(cors());                                          app.use(cors());
var urlencodedParser = bodyParser.urlencoded({ extended: false });
                                                         
app.use(bodyParser.json());                               app.use(bodyParser.json());
app.use(urlencodedParser);                                app.use(urlencodedParser);

                                                         // Setup rotating log stream
                                                         const logDirectory = path.join(__dirname, '..', 'log');
                                                         if (!fs.existsSync(logDirectory)) {
                                                             fs.mkdirSync(logDirectory);
                                                         }
                                                         const accessLogStream = rfs.createStream('log.txt', {
                                                             interval: '12h',
                                                             path: logDirectory,
                                                         });

                                                         // Custom token for exceptions
                                                         morgan.token('exception', (req, res) => res.locals.errorMessage || '-');

                                                         // JSON log format
                                                         morgan.format('jsonFormat', (tokens, req, res) => {
                                                             return JSON.stringify({
                                                                 exception: tokens.exception(req, res),
                                                                 method: req.method,
                                                                 url: req.originalUrl,
                                                                 ip: req.ip,
                                                                 date: new Date().toUTCString()
                                                             });
                                                         });

                                                         // Apply logger middleware
                                                         app.use(morgan('jsonFormat', { stream: accessLogStream }));
                                                         app.use(morgan('jsonFormat')); // Also print to console

app.get('/user/:userid', function (req, res) {            app.get('/user/:userid', function (req, res) {
    var id = req.params.userid;                               var id = req.params.userid;

    user.getUser(id, function (err, result) {                 user.getUser(id, function (err, result) {
        if (!err) {                                               if (!err) {
            //validateFn.sanitizeResult(result);                       res.send(result);
            res.send(result);                                      } else {
        } else {                                                       res.locals.errorMessage = err.toString(); // store error
            res.status(500).send("Some error");                     res.status(500).send("Some error");
        }                                                            }
    });                                                          });
});                                                           });

app.get('/user', function (req, res) {                    app.get('/user', function (req, res) {
    user.getUsers(function (err, result) {                    user.getUsers(function (err, result) {
        if (!err) {                                               if (!err) {
            //validateFn.sanitizeResult(result);                   res.send(result);
            res.send(result);                                  } else {
        } else {                                                   res.locals.errorMessage = err.toString(); // store error
            res.status(500).send(null);                           res.status(500).send(null);
        }                                                        }
    });                                                      });
});                                                       });

module.exports = app;                                    module.exports = app;
