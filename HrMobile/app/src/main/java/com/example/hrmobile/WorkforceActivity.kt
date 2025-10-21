package com.example.hrmobile

import android.os.Bundle
import android.widget.CalendarView
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.text.SimpleDateFormat
import java.util.*

class WorkforceActivity : AppCompatActivity() {

    private lateinit var btnBack: ImageView
    private lateinit var calendarView: CalendarView

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_workforce)

        // Initialize views
        btnBack = findViewById(R.id.btnBack)
        calendarView = findViewById(R.id.calendarView)

        // Back button functionality
        btnBack.setOnClickListener {
            finish() // Go back to Dashboard
        }

        // Set up calendar view
        setupCalendarView()
    }

    private fun setupCalendarView() {
        // Set the current date
        calendarView.date = System.currentTimeMillis()

        // Set minimum date (optional - set to 1 year ago)
        val minCalendar = Calendar.getInstance()
        minCalendar.add(Calendar.YEAR, -1)
        calendarView.minDate = minCalendar.timeInMillis

        // Set maximum date (optional - set to 1 year ahead)
        val maxCalendar = Calendar.getInstance()
        maxCalendar.add(Calendar.YEAR, 1)
        calendarView.maxDate = maxCalendar.timeInMillis

        // Set listener for date selection
        calendarView.setOnDateChangeListener { _, year, month, dayOfMonth ->
            val selectedCalendar = Calendar.getInstance()
            selectedCalendar.set(year, month, dayOfMonth)
            val selectedDate = dateFormat.format(selectedCalendar.time)

            // Show selected date
            Toast.makeText(
                this,
                "Selected Date: $selectedDate",
                Toast.LENGTH_SHORT
            ).show()

            // TODO: Load events for selected date from database or API
            // You can implement this to show events for the selected date
            loadEventsForDate(selectedDate)
        }
    }

    private fun loadEventsForDate(date: String) {
        // TODO: Implement loading events from database or API
        // This is where you would fetch and display events for the selected date

        // Example: Check if there are any events for this date
        val events = getEventsForDate(date)

        if (events.isNotEmpty()) {
            // Show events
            Toast.makeText(
                this,
                "Events on $date: ${events.joinToString(", ")}",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    private fun getEventsForDate(date: String): List<String> {
        // Sample hardcoded events - Replace with actual database query
        val eventsMap = mapOf(
            "2024-01-16" to listOf("Team Meeting"),
            "2024-01-18" to listOf("Training Session"),
            "2024-01-20" to listOf("Annual Leave - John"),
            "2024-01-22" to listOf("Project Deadline")
        )

        return eventsMap[date] ?: emptyList()
    }
}