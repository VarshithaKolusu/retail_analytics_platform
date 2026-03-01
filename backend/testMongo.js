const { MongoClient } = require("mongodb");

const client = new MongoClient("mongodb+srv://RETAILdb:sneha112006@retaildashboardcluster.hejud1k.mongodb.net/");

client.connect()
  .then(() => {
    console.log("MongoDB connected!");
    client.close();
  })
  .catch(err => console.error("MongoDB connection failed:", err));