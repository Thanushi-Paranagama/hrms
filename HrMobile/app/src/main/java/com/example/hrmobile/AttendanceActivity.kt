package com.example.hrmobile

import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.text.SimpleDateFormat
import java.util.*

class AttendanceActivity : AppCompatActivity() {

    private lateinit var btnBack: ImageView
    private lateinit var tvCurrentDate: TextView
    private lateinit var tvCurrentTime: TextView
    private lateinit var btnStartVerification: Button
    private lateinit var tvCheckIn: TextView
    private lateinit var tvCheckOut: TextView
    private lateinit var tvLocation: TextView
    private lateinit var tvStatus: TextView

    private var isCheckedIn = false
    private var checkInTime: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_attendance)

        // Initialize views
        btnBack = findViewById(R.id.btnBack)
        tvCurrentDate = findViewById(R.id.tvCurrentDate)
        tvCurrentTime = findViewById(R.id.tvCurrentTime)
        btnStartVerification = findViewById(R.id.btnStartVerification)
        tvCheckIn = findViewById(R.id.tvCheckIn)
        tvCheckOut = findViewById(R.id.tvCheckOut)
        tvLocation = findViewById(R.id.tvLocation)
        tvStatus = findViewById(R.id.tvStatus)

        // Set current date and time
        updateDateTime()

        // Start a timer to update time every second
        startTimeUpdater()

        // Back button functionality
        btnBack.setOnClickListener {
            finish() // Go back to previous activity (Dashboard)
        }

        // Start face verification button
        btnStartVerification.setOnClickListener {
            startFaceVerification()
        }
    }

    private fun updateDateTime() {
        val calendar = Calendar.getInstance()

        // Format date
        val dateFormat = SimpleDateFormat("MM/dd/yyyy", Locale.getDefault())
        val currentDate = dateFormat.format(calendar.time)
        tvCurrentDate.text = "Current Date: $currentDate"

        // Format time
        val timeFormat = SimpleDateFormat("hh:mm:ss a", Locale.getDefault())
        val currentTime = timeFormat.format(calendar.time)
        tvCurrentTime.text = "Current Time: $currentTime"
    }

    private fun startTimeUpdater() {
        val handler = android.os.Handler(mainLooper)
        handler.post(object : Runnable {
            override fun run() {
                updateDateTime()
                handler.postDelayed(this, 1000) // Update every second
            }
        })
    }

    private fun startFaceVerification() {
        // Simulate face verification process
        Toast.makeText(this, "Starting face verification...", Toast.LENGTH_SHORT).show()

        // Simulate a delay for face recognition
        android.os.Handler(mainLooper).postDelayed({
            // For demo purposes, automatically verify as successful
            onVerificationSuccess()
        }, 2000) // 2 second delay

        // TODO: Implement actual face recognition here
        // You can integrate ML Kit Face Detection or other face recognition libraries
    }

    private fun onVerificationSuccess() {
        val currentTime = SimpleDateFormat("hh:mm:ss a", Locale.getDefault()).format(Date())
        val location = "Office - Main Branch" // You can implement actual location tracking

        if (!isCheckedIn) {
            // Check In
            isCheckedIn = true
            checkInTime = currentTime
            tvCheckIn.text = currentTime
            tvLocation.text = location
            tvStatus.text = "Checked In"
            tvStatus.setTextColor(getColor(android.R.color.holo_green_dark))
            btnStartVerification.text = "Check Out"

            Toast.makeText(this, "Check-in successful!", Toast.LENGTH_SHORT).show()
        } else {
            // Check Out
            tvCheckOut.text = currentTime
            tvStatus.text = "Completed"
            tvStatus.setTextColor(getColor(android.R.color.holo_blue_dark))
            btnStartVerification.isEnabled = false
            btnStartVerification.alpha = 0.5f

            Toast.makeText(this, "Check-out successful!", Toast.LENGTH_SHORT).show()

            // Optional: Show attendance summary
            showAttendanceSummary()
        }
    }

    private fun showAttendanceSummary() {
        // Calculate work duration
        // You can implement actual duration calculation here
        Toast.makeText(
            this,
            "Attendance marked successfully!\nCheck-in: $checkInTime\nCheck-out: ${tvCheckOut.text}",
            Toast.LENGTH_LONG
        ).show()

        // Optional: Navigate back to dashboard after a delay
        android.os.Handler(mainLooper).postDelayed({
            finish()
        }, 3000)
    }
}