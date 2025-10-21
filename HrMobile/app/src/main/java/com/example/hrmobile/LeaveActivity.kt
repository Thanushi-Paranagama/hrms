package com.example.hrmobile

import android.app.DatePickerDialog
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import java.text.SimpleDateFormat
import java.util.*

class LeaveActivity : AppCompatActivity() {

    private lateinit var btnBack: ImageButton
    private lateinit var spinnerLeaveType: Spinner
    private lateinit var etFromDate: EditText
    private lateinit var etToDate: EditText
    private lateinit var etReason: EditText
    private lateinit var btnSubmit: Button

    private val calendar = Calendar.getInstance()
    private val dateFormat = SimpleDateFormat("MM/dd/yyyy", Locale.getDefault())

    private var fromDate: Calendar? = null
    private var toDate: Calendar? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_leave)

        // Initialize views
        btnBack = findViewById(R.id.btnBack)
        spinnerLeaveType = findViewById(R.id.spinnerLeaveType)
        etFromDate = findViewById(R.id.etFromDate)
        etToDate = findViewById(R.id.etToDate)
        etReason = findViewById(R.id.etReason)
        btnSubmit = findViewById(R.id.btnSubmit)

        // Setup Leave Type Spinner
        setupLeaveTypeSpinner()

        // Back button functionality
        btnBack.setOnClickListener {
            finish() // Go back to Dashboard
        }

        // From Date picker
        etFromDate.setOnClickListener {
            showDatePicker(true)
        }

        // To Date picker
        etToDate.setOnClickListener {
            showDatePicker(false)
        }

        // Submit button
        btnSubmit.setOnClickListener {
            submitLeaveRequest()
        }
    }

    private fun setupLeaveTypeSpinner() {
        // Define leave types
        val leaveTypes = arrayOf(
            "Select Leave Type",
            "Annual Leave",
            "Sick Leave",
            "Casual Leave",
            "Medical Leave",
            "Emergency Leave",
            "Maternity Leave",
            "Paternity Leave",
            "Unpaid Leave"
        )

        // Create adapter
        val adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_item,
            leaveTypes
        )
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)

        // Set adapter to spinner
        spinnerLeaveType.adapter = adapter
    }

    private fun showDatePicker(isFromDate: Boolean) {
        val currentCalendar = if (isFromDate) {
            fromDate ?: Calendar.getInstance()
        } else {
            toDate ?: fromDate ?: Calendar.getInstance()
        }

        val datePickerDialog = DatePickerDialog(
            this,
            { _, year, month, dayOfMonth ->
                val selectedCalendar = Calendar.getInstance()
                selectedCalendar.set(year, month, dayOfMonth)

                if (isFromDate) {
                    fromDate = selectedCalendar
                    etFromDate.setText(dateFormat.format(selectedCalendar.time))

                    // Clear toDate if it's before fromDate
                    if (toDate != null && toDate!!.before(selectedCalendar)) {
                        toDate = null
                        etToDate.setText("")
                    }
                } else {
                    // Validate that toDate is not before fromDate
                    if (fromDate != null && selectedCalendar.before(fromDate)) {
                        Toast.makeText(
                            this,
                            "To Date cannot be before From Date",
                            Toast.LENGTH_SHORT
                        ).show()
                        return@DatePickerDialog
                    }

                    toDate = selectedCalendar
                    etToDate.setText(dateFormat.format(selectedCalendar.time))
                }
            },
            currentCalendar.get(Calendar.YEAR),
            currentCalendar.get(Calendar.MONTH),
            currentCalendar.get(Calendar.DAY_OF_MONTH)
        )

        // Set minimum date for toDate picker
        if (!isFromDate && fromDate != null) {
            datePickerDialog.datePicker.minDate = fromDate!!.timeInMillis
        } else {
            // Set minimum date to today for fromDate
            datePickerDialog.datePicker.minDate = System.currentTimeMillis() - 1000
        }

        datePickerDialog.show()
    }

    private fun submitLeaveRequest() {
        // Get values
        val leaveType = spinnerLeaveType.selectedItem.toString()
        val fromDateText = etFromDate.text.toString().trim()
        val toDateText = etToDate.text.toString().trim()
        val reason = etReason.text.toString().trim()

        // Validate inputs
        if (leaveType == "Select Leave Type") {
            Toast.makeText(this, "Please select a leave type", Toast.LENGTH_SHORT).show()
            return
        }

        if (fromDateText.isEmpty()) {
            Toast.makeText(this, "Please select from date", Toast.LENGTH_SHORT).show()
            etFromDate.requestFocus()
            return
        }

        if (toDateText.isEmpty()) {
            Toast.makeText(this, "Please select to date", Toast.LENGTH_SHORT).show()
            etToDate.requestFocus()
            return
        }

        if (reason.isEmpty()) {
            Toast.makeText(this, "Please provide reason for leave", Toast.LENGTH_SHORT).show()
            etReason.requestFocus()
            return
        }

        if (reason.length < 10) {
            Toast.makeText(this, "Please provide a detailed reason (at least 10 characters)", Toast.LENGTH_SHORT).show()
            etReason.requestFocus()
            return
        }

        // Calculate number of days
        val days = calculateDays()

        // Show confirmation dialog
        showConfirmationDialog(leaveType, fromDateText, toDateText, days, reason)
    }

    private fun calculateDays(): Int {
        if (fromDate == null || toDate == null) return 0

        val diff = toDate!!.timeInMillis - fromDate!!.timeInMillis
        return (diff / (1000 * 60 * 60 * 24)).toInt() + 1
    }

    private fun showConfirmationDialog(
        leaveType: String,
        fromDate: String,
        toDate: String,
        days: Int,
        reason: String
    ) {
        val message = """
            Leave Type: $leaveType
            From: $fromDate
            To: $toDate
            Duration: $days day(s)
            
            Reason: $reason
            
            Do you want to submit this leave request?
        """.trimIndent()

        AlertDialog.Builder(this)
            .setTitle("Confirm Leave Request")
            .setMessage(message)
            .setPositiveButton("Submit") { dialog, _ ->
                // TODO: Save to database or send to API
                Toast.makeText(
                    this,
                    "Leave request submitted successfully!",
                    Toast.LENGTH_LONG
                ).show()

                // Clear form
                clearForm()

                dialog.dismiss()

                // Navigate back to dashboard after a delay
                android.os.Handler(mainLooper).postDelayed({
                    finish()
                }, 1500)
            }
            .setNegativeButton("Cancel") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }

    private fun clearForm() {
        spinnerLeaveType.setSelection(0)
        etFromDate.setText("")
        etToDate.setText("")
        etReason.setText("")
        fromDate = null
        toDate = null
    }
}