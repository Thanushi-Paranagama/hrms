package com.example.hrmobile

import android.content.Intent
import android.os.Bundle
import android.util.Patterns
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

class RegistrationActivity : AppCompatActivity() {

    private lateinit var backButton: ImageButton
    private lateinit var fullNameInput: TextInputEditText
    private lateinit var emailInput: TextInputEditText
    private lateinit var usernameInput: TextInputEditText
    private lateinit var passwordInput: TextInputEditText
    private lateinit var confirmPasswordInput: TextInputEditText
    private lateinit var registerButton: MaterialButton
    private lateinit var loginLink: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_registration)

        // Initialize views
        backButton = findViewById(R.id.backButton)
        fullNameInput = findViewById(R.id.fullNameInput)
        emailInput = findViewById(R.id.emailInput)
        usernameInput = findViewById(R.id.usernameInput)
        passwordInput = findViewById(R.id.passwordInput)
        confirmPasswordInput = findViewById(R.id.confirmPasswordInput)
        registerButton = findViewById(R.id.registerButton)
        loginLink = findViewById(R.id.loginLink)

        // Back button functionality
        backButton.setOnClickListener {
            finish() // Go back to login screen
        }

        // Register button click listener
        registerButton.setOnClickListener {
            handleRegistration()
        }

        // Login link click listener
        loginLink.setOnClickListener {
            finish() // Go back to login screen
        }
    }

    private fun handleRegistration() {
        val fullName = fullNameInput.text.toString().trim()
        val email = emailInput.text.toString().trim()
        val username = usernameInput.text.toString().trim()
        val password = passwordInput.text.toString().trim()
        val confirmPassword = confirmPasswordInput.text.toString().trim()

        // Validate Full Name
        if (fullName.isEmpty()) {
            fullNameInput.error = "Full name is required"
            fullNameInput.requestFocus()
            return
        }

        if (fullName.length < 3) {
            fullNameInput.error = "Full name must be at least 3 characters"
            fullNameInput.requestFocus()
            return
        }

        // Validate Email
        if (email.isEmpty()) {
            emailInput.error = "Email is required"
            emailInput.requestFocus()
            return
        }

        if (!Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            emailInput.error = "Please enter a valid email"
            emailInput.requestFocus()
            return
        }

        // Validate Username
        if (username.isEmpty()) {
            usernameInput.error = "Username is required"
            usernameInput.requestFocus()
            return
        }

        if (username.length < 4) {
            usernameInput.error = "Username must be at least 4 characters"
            usernameInput.requestFocus()
            return
        }

        // Check if username contains only alphanumeric characters
        if (!username.matches(Regex("^[a-zA-Z0-9_]+$"))) {
            usernameInput.error = "Username can only contain letters, numbers, and underscores"
            usernameInput.requestFocus()
            return
        }

        // Validate Password
        if (password.isEmpty()) {
            passwordInput.error = "Password is required"
            passwordInput.requestFocus()
            return
        }

        if (password.length < 6) {
            passwordInput.error = "Password must be at least 6 characters"
            passwordInput.requestFocus()
            return
        }

        // Validate Confirm Password
        if (confirmPassword.isEmpty()) {
            confirmPasswordInput.error = "Please confirm your password"
            confirmPasswordInput.requestFocus()
            return
        }

        if (password != confirmPassword) {
            confirmPasswordInput.error = "Passwords do not match"
            confirmPasswordInput.requestFocus()
            return
        }

        // Check if username already exists (replace with actual database check)
        if (isUsernameExists(username)) {
            usernameInput.error = "Username already exists"
            usernameInput.requestFocus()
            return
        }

        // Check if email already exists (replace with actual database check)
        if (isEmailExists(email)) {
            emailInput.error = "Email already registered"
            emailInput.requestFocus()
            return
        }

        // All validations passed - proceed with registration
        registerUser(fullName, email, username, password)
    }

    private fun isUsernameExists(username: String): Boolean {
        // TODO: Replace with actual database check
        // For now, check against hardcoded usernames
        val existingUsernames = listOf("admin", "user1", "1212")
        return existingUsernames.contains(username)
    }

    private fun isEmailExists(email: String): Boolean {
        // TODO: Replace with actual database check
        // For now, return false to allow registration
        return false
    }

    private fun registerUser(fullName: String, email: String, username: String, password: String) {
        // TODO: Save user to database or send to API
        // For now, just show success message

        Toast.makeText(
            this,
            "Registration Successful!\nWelcome, $fullName",
            Toast.LENGTH_LONG
        ).show()

        // Clear form
        clearForm()

        // Navigate back to login screen after a delay
        android.os.Handler(mainLooper).postDelayed({
            finish()
        }, 2000)

        // Optional: Auto-login after registration
        // navigateToLogin(username, password)
    }

    private fun clearForm() {
        fullNameInput.setText("")
        emailInput.setText("")
        usernameInput.setText("")
        passwordInput.setText("")
        confirmPasswordInput.setText("")
    }

    private fun navigateToLogin(username: String, password: String) {
        // Optional: Pass credentials back to login screen for auto-login
        val intent = Intent(this, MainActivity::class.java)
        intent.putExtra("USERNAME", username)
        intent.putExtra("PASSWORD", password)
        intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
        startActivity(intent)
        finish()
    }
}