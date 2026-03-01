// routes/data.js
const express = require("express");
const router = express.Router();
const multer = require("multer"); // for handling file uploads
const csv = require("csvtojson");
const jwt = require("jsonwebtoken");
const SECRET_KEY = "YOUR_SECRET_KEY";


// Multer setup for CSV upload
const storage = multer.memoryStorage();
const upload = multer({ storage });

// Middleware to verify JWT
const authMiddleware = (req, res, next) => {
  const token = req.headers["authorization"];
  if (!token) return res.status(401).json({ message: "No token provided" });

  try {
    const decoded = jwt.verify(token.split(" ")[1], SECRET_KEY);
    req.userId = decoded.userId;
    next();
  } catch (err) {
    return res.status(401).json({ message: "Invalid token" });
  }
};

// Upload CSV endpoint
router.post("/upload_csv", authMiddleware, upload.single("file"), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ message: "No file uploaded" });

    const csvString = req.file.buffer.toString("utf-8");
    const data = await csv().fromString(csvString);

    // Example KPI calculations
    let totalRevenue = 0, totalProfit = 0;
    let productSales = {};

    data.forEach(row => {
      const revenue = parseFloat(row.Revenue) || 0;
      const profit = parseFloat(row.Profit) || 0;
      totalRevenue += revenue;
      totalProfit += profit;

      const product = row.Product || "Unknown";
      productSales[product] = (productSales[product] || 0) + revenue;
    });

    const profitMargin = totalRevenue ? (totalProfit / totalRevenue) * 100 : 0;

    // Store dataset
    const datasetResult = await datasetsCollection.insertOne({
      userId: ObjectId(req.userId),
      rawCsv: csvString,
      createdAt: new Date()
    });

    // Store metrics
    const metricsResult = await metricsCollection.insertOne({
      datasetId: datasetResult.insertedId,
      totalRevenue,
      totalProfit,
      profitMargin,
      topProducts: Object.entries(productSales)
        .sort((a,b) => b[1]-a[1])
        .slice(0,5),
      createdAt: new Date()
    });

    res.json({
      message: "CSV uploaded and metrics calculated",
      metrics: {
        totalRevenue,
        totalProfit,
        profitMargin,
        topProducts: Object.entries(productSales)
          .sort((a,b) => b[1]-a[1])
          .slice(0,5)
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
});

// Get dashboard metrics
router.get("/get_dashboard", authMiddleware, async (req, res) => {
  try {
    const metrics = await metricsCollection.find({}).toArray();
    res.json(metrics);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
});

module.exports = router;