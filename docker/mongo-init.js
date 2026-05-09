db = db.getSiblingDB("arl");
try { db.user.drop(); } catch(e) {}
const crypto = require("crypto");
db.user.insertOne({
    username: "admin",
    password: crypto.createHash("md5").update("arlsalt!@#arlpass").digest("hex")
});
