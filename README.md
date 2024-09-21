# Django Room Booking App

## Overview
This is a Django-based room booking system that allows users to browse rooms, make bookings, leave reviews, and manage their profiles. The app also integrates Stripe for payment processing.\

## Creation
This is a simple project I created to learn some interesting things about Django and webapp development. I would say that I've learned quite a bit throughout the process. There were a lot of difficult parts in breaking down how to best approach each part of the project, but for the most part I found it to be a very enjoyable simple project to create. I wanted to model it as if it was a simple app like Booking.com or AirBnB, and I believe it went reasonably well. 

## Features
- **User Authentication**: Users can create accounts, log in, and manage their profiles.
- **Room Browsing**: Users can view rooms by location, discounted rates, and availability.
- **Room Booking**: Users can book available rooms and view their booking history.
- **Payment Processing**: Integration with Stripe to handle secure payments.
- **Reviews**: Users can leave reviews for the rooms they've booked.
- **Search**: Users can search for rooms by location, price range, and number of bedrooms.
- **Featured Rooms**: Displays rooms from random cities for users to explore.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add the following variables:
      ```bash
      STRIPE_SECRET_KEY=<your-stripe-secret-key>
      ```

4. Run migrations:
    ```bash
    python manage.py migrate
    ```

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

- **Homepage**: Displays featured rooms from random cities.
- **Room Browsing**: Explore available rooms, apply filters for location, price, and number of rooms.
- **Booking**: Select check-in and check-out dates, proceed with Stripe for payment.
- **Profile**: Manage profile information and view booking history.
- **Review**: Submit reviews for rooms after staying.
- **Search**: Find rooms based on location, price range, and more.

## Stripe Integration

The app uses Stripe for payment processing. Make sure to replace `STRIPE_SECRET_KEY` with your actual Stripe API keys in the environment variables.

## URLs

- `/` - Homepage with featured rooms
- `/rooms/` - List of all rooms
- `/room/<int:pk>/` - Detailed view of a specific room
- `/user/` - User profile page
- `/booking/history/` - View booking history
- `/discounted-rooms/` - View rooms with discounts
- `/payment/success/` - Payment success page
- `/payment/failed/` - Payment failure page

## Models

- **User**: Custom user model with profile pictures and ratings.
- **RoomItem**: Represents rooms available for booking.
- **Booking**: Stores booking details including check-in/check-out dates and payment status.
- **Payment**: Handles payment processing information for each booking.
- **Review**: User reviews for rooms.
- **Address**: Stores the address information for rooms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
