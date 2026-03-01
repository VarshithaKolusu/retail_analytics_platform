const { MongoClient } = require("mongodb");

const uri = "mongodb+srv://RETAILdb:sneha112006@retaildashboardcluster.hejud1k.mongodb.net/";

const client = new MongoClient(uri);

async function connectDB() {
  try {
    await client.connect();
    console.log("Connected to MongoDB Atlas");
  } catch (err) {
    console.error("MongoDB connection error:", err);
  }
}

connectDB();

const db = client.db("retail_dashboard");

// server.js
const express = require("express");
const cors = require("cors");

const authRoutes = require("./routes/auth"); // auth routes
const dataRoutes = require("./routes/data"); // data routes

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Use routes
app.use("/api/auth", authRoutes);
app.use("/api/data", dataRoutes);

// Start server
const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));