package com.example.hrmobile

import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.text.NumberFormat
import java.util.*

class ReportsActivity : AppCompatActivity() {

    private lateinit var btnBack: ImageView
    private lateinit var tvTotalWorkingDays: TextView
    private lateinit var tvPresentDays: TextView
    private lateinit var tvBaseSalary: TextView
    private lateinit var tvCalculatedSalary: TextView

    // Sample data - Replace with actual data from database or API
    private val totalWorkingDays = 22
    private val presentDays = 20
    private val baseSalary = 5000.0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_reports)

        // Initialize views
        btnBack = findViewById(R.id.btnBack)
        tvTotalWorkingDays = findViewById(R.id.tvTotalWorkingDays)
        tvPresentDays = findViewById(R.id.tvPresentDays)
        tvBaseSalary = findViewById(R.id.tvBaseSalary)
        tvCalculatedSalary = findViewById(R.id.tvCalculatedSalary)

        // Back button functionality
        btnBack.setOnClickListener {
            finish() // Go back to Dashboard
        }

        // Load and display data
        loadReportData()
    }

    private fun loadReportData() {
        // Display total working days
        tvTotalWorkingDays.text = totalWorkingDays.toString()

        // Display present days
        tvPresentDays.text = presentDays.toString()

        // Format and display base salary
        val currencyFormat = NumberFormat.getCurrencyInstance(Locale.US)
        tvBaseSalary.text = currencyFormat.format(baseSalary)

        // Calculate and display calculated salary
        val calculatedSalary = calculateSalary(baseSalary, totalWorkingDays, presentDays)
        tvCalculatedSalary.text = currencyFormat.format(calculatedSalary)
    }

    /**
     * Calculate salary based on present days
     * Formula: (Base Salary / Total Working Days) * Present Days
     */
    private fun calculateSalary(baseSalary: Double, totalDays: Int, presentDays: Int): Double {
        if (totalDays == 0) return 0.0

        val perDaySalary = baseSalary / totalDays
        return perDaySalary * presentDays
    }
}