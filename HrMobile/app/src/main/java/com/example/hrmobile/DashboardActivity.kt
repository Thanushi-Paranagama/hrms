package com.example.hrmobile

import android.content.Intent
import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView

class DashboardActivity : AppCompatActivity() {

    private lateinit var tvWelcome: TextView
    private lateinit var btnMarkAttendance: CardView
    private lateinit var btnLeaveRequest: CardView
    private lateinit var btnWorkforceCalendar: CardView
    private lateinit var btnReportsAnalytics: CardView
    private lateinit var logoutIcon: ImageView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Initialize views
        tvWelcome = findViewById(R.id.tvWelcome)
        btnMarkAttendance = findViewById(R.id.btnMarkAttendance)
        btnLeaveRequest = findViewById(R.id.btnLeaveRequest)
        btnWorkforceCalendar = findViewById(R.id.btnWorkforceCalendar)
        btnReportsAnalytics = findViewById(R.id.btnReportsAnalytics)

        // Get username from intent
        val username = intent.getStringExtra("USERNAME") ?: "User"
        tvWelcome.text = "Welcome back, $username"

        // Set up button click listeners
        btnMarkAttendance.setOnClickListener {
            // Navigate to Mark Attendance activity
            val intent = Intent(this, AttendanceActivity::class.java)
            startActivity(intent)
        }

        btnLeaveRequest.setOnClickListener {
            // Navigate to Leave Request activity
            val intent = Intent(this, LeaveActivity::class.java)
            startActivity(intent)
        }

        btnWorkforceCalendar.setOnClickListener {
            // Navigate to Reports & Analytics activity
            val intent = Intent(this, WorkforceActivity::class.java)
            startActivity(intent)
        }

        btnReportsAnalytics.setOnClickListener {
            // Navigate to Reports & Analytics activity
            val intent = Intent(this, ReportsActivity::class.java)
            startActivity(intent)
        }

        // Logout functionality
        // Find the logout icon and set click listener
        try {
            logoutIcon = findViewById(R.id.logoutIcon)
            logoutIcon.setOnClickListener {
                handleLogout()
            }
        } catch (e: Exception) {
            // If logout icon doesn't have an ID, you'll need to add it
        }
    }

    private fun handleLogout() {
        // Clear any saved session data here if needed
        Toast.makeText(this, "Logged out successfully", Toast.LENGTH_SHORT).show()

        // Navigate back to login
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}