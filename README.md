# Overview
Welcome to the **E-Commerce API** documentation. This document provides a detailed walkthrough of the API, including available endpoints, authentication requirements, and usage examples.
# Introduction
The **E-Commerce API** enables users to perform various e-commerce-related actions, such as: 
- Browsing a catalog of products. 
- Adding items to a cart or wishlist. 
- Purchasing items securely. 
- Managing user profiles and orders.
# Authentication
This API uses Django's token based authentication. Include the token in the `Authorization` header of each request. **Example Header:** 
```http 
Authorization: Token YOUR_ACCESS_TOKEN
```
# List of All Endpoints
### Authentication
---
- `POST` - `https://isri21.pythonanywhere.com/auth/register/`
- `GET` - `https://isri21.pythonanywhere.com/login/`
### Store
- `GET` - `https://isri21.pythonanywhere.com`
- `GET` - `https://isri21.pythonanywhere.com/products/<id>/`
- `GET` - `https://isri21.pythonanywhere.com/products/<id>/reviews/`
- `POST` - `https://isri21.pythonanywhere.com/products/<id>/`
- `POST` - `https://isri21.pythonanywhere.com/products/<id>/wishlist/`
- `POST` - `https://isri21.pythonanywhere.com/products/<id>/review/`
- `POST` - `https://isri21.pythonanywhere.com/products/<id>/rate/`
- `GET` - `https://isri21.pythonanywhere.com/categories/`
### Account
- `GET` - `https://isri21.pythonanywhere.com/account/`
- `PATCH` - `https://isri21.pythonanywhere.com/account/`
- `GET` - `https://isri21.pythonanywhere.com/account/categories/`
- `POST` - `https://isri21.pythonanywhere.com/account/categories/`
- `PUT` - `https://isri21.pythonanywhere.com/account/categories/<id>/`
- `DELETE` - `https://isri21.pythonanywhere.com/account/categories/<id>/`
- `GET` - `https://isri21.pythonanywhere.com/account/wishlist/`
- `DELETE` - `https://isri21.pythonanywhere.com/account/wishlist/<id>/`
- `GET` - `https://isri21.pythonanywhere.com/account/purchases/`
- `GET` - `https://isri21.pythonanywhere.com/account/reviews/`
- `PUT` - `https://isri21.pythonanywhere.com/account/reviews/<id>/`
- `DELETE` - `https://isri21.pythonanywhere.com/account/reviews/<id>/`
- `GET` - `https://isri21.pythonanywhere.com/account/ratings/`
- `PUT` - `https://isri21.pythonanywhere.com/account/ratings/<id>/`
- `DELETE` - `https://isri21.pythonanywhere.com/account/ratings/<id>/`
- `GET` - `https://isri21.pythonanywhere.com/account/products/`
- `POST` - `https://isri21.pythonanywhere.com/account/products/`
- `PATCH` - `https://isri21.pythonanywhere.com/account/products/<id>/`
- `DELETE` - `https://isri21.pythonanywhere.com/account/products/<id>/`


# Authentication Endpoints
## User Registration
- **Endpoint**: `https://isri21.pythonanywhere.com/auth/register/` 
- **Method**: `POST`
- **Description**: Register an new user.
### Body Parameter

| Parameter          | Type  | Required | Description                                     |
| ------------------ | ----- | -------- | ----------------------------------------------- |
| `username`         | `str` | Yes      | Username of the user. **Must be unique.**       |
| `first_name`       | `str` | No       | The first name of the user.                     |
| `last_name`        | `str` | No       | The last name of the user.                      |
| `email`            | `str` | No       | The email of the user.                          |
| `password`         | `str` | Yes      | Strong password for the user.                   |
| `confirm_password` | `str` | Yes      | Value must be the same as the `password` field. |

#### Example Request Body
```json
{
    "username": "kebede",
    "first_name": "Kebede",
    "last_name": "Bekele",
    "email": "kebede@email.com",
    "password": "securepasswd",
    "confirm_password": "securepasswd"
}
```
### Responses
#### `201 Created`
The user was successfully created.
```json
{
	"status": "You have successfully registered!",
	"token": "0299e50b29bad987b6fca86d442b5ef8dc950e87"
}
```
#### `400 Bad Request`
- If fields not specified.
```json
{
	"username": [
		"This field is required."
	],
	"password": [
		"This field is required."
	],
	"confirm_password": [
		"This field is required."
	]
}
```
- If the passwords provided do not match.
```json
{
	"password": [
		"The passwords provided do not match."
	]
}
```
- If the user already exists.
```json
{
	"username": [
		"A user with that username already exists."
	]
}
```
## User Login
- **Endpoint**: `https://isri21.pythonanywhere.com/login/`
- **Method**: `GET`
- **Description**: Obtain an authorization token.
### Request Body
```json
{
	"username": "abebe",
	"password": "securepassword"
}
```

### Responses
#### `200 OK`
Returns the user's authentication token.
```json
{
	"token": "0299e50b29bad987b6fca86d442b5ef8dc950e87"
}
```
#### `400 Bad Request`
```json
{
	"error": "Incorrect username or password!"
}
```
# Store Endpoints
## Get All Products
**URL**: `https://isri21.pythonanywhere.com`
**Method**: `GET`
**Description**: User can get a list f all the products in the store.
### Query Parameters

| Parameter   | Type   | Required | Description                                                                                      | Default | Example            |
| ----------- | ------ | -------- | ------------------------------------------------------------------------------------------------ | ------- | ------------------ |
| `search`    | `str`  | No       | Enables to search the products in the store by product name or category.                         | `All`   | `?search=phone`    |
| `page`      | `int`  | No       | Specifying the page number for paginating the products in the store.                             | `1`     | `?page=2`          |
| `per_page`  | `int`  | No       | Control the number of product items per page.                                                    | `5`     | `?page_size=2`     |
| `category`  | `str`  | No       | Filter the products in the store by their category.                                              | `All`   | `?category=mobile` |
| `min_price` | `int`  | No       | Filter the products in the store above a given price                                             | `All`   | `?min_price=1000`  |
| `max_price` | `int`  | No       | Filter the products in the store below a given price                                             | `All`   | `?max_price=1000`  |
| `in_stock`  | `bool` | No       | Filter the products in the store based on their stock availability. Can only enter `no` or `yes` | `All`   | `?in_stock=yes`    |
#### Example Query
```url
https://isri21.pythonanywhere.com/?search=phone&category=mobile&in_stock=yes
```
### Response
#### `200 OK`
Returns all the products in the store, or returns the products as specified in the query parameters.
```json
{
	"total_products": 200,
	"total_pages": 100,
	"current_page": 1,
	"products_per_page": 2,
	"next_page": "http://isri21.pythonanywhere.com/https://isri21.pythonanywhere.com/products/?page=2",
	"previous_page": null,
	"results": [
	{
		"id": 1,
		"name": "IPhone Charger",
		"images": [
			"/products/1/image1.jpg",
			"/products/1/image2.jpg"
		],
		"category": [
			"Mobile", 
			"Electronics"
		],
		"stock_quantity": 12		
	},
	{
		"id": 2,
		"name": "Samsung Charger",
		"images": [
			"/products/2/image1.jpg",
			"/products/2/image2.jpg"
		],
		"category": [
			"Mobile",
			"Electronics"
		],
		"stock_quantity": 10		
	}
	]
}
```
#### `400 Bad Request`
- If an invalid query parameter is specified.
```json
{
	"{query_param}": "Invalid query parameter"
}
```
- If the value of `in_stock` query parameter is not `yes` or `no`.
```json
{
	"in_stock": "The in_stock filter must be a 'yes' or 'no' value!"
}
```
- If the value for `min_price` only is not a number.
```json
{
	"min_price": "The min_price query must be a float or an integer value."
}
```
- If the value for `max_price` only is not a number.
```json
{
	"max_price": "The max_price query must be a float or an integer value."
}
```
- If the values for `min_price` or `max_price` are not numbers.
```json
{
	"range_error": "Both the min_price and max_price filters must be numbers."
}
```
- If both the `min_price` and `max_price` are specified, but the `min_price` is greater than the `max_price`.
```json
{
	"range_error": "The minimum price, can not be greater than the maximum price"
}
```
#### `404 Not Found`
- If there are not items that match the filters specified in the query parameters.
```json
{
	"error": "There are no items that match your filters."
}
```
## Get Specific Product
**URL**: `https://isri21.pythonanywhere.com/products/<id>/`
**Method**: `GET`
**Description**: User can get the details for a specific product.
### Path Parameters

| Parameter | Type  | Required | Description              |
| --------- | ----- | -------- | ------------------------ |
| `{id}`    | `int` | Yes      | The `id` of the product. |
#### Example Path
```https
https://isri21.pythonanywhere.com/products/1/
```
### Responses
#### `200 OK`
```json
{
	"product_details": {
		"id": 1,
		"owner": "root",
		"name": "I Phone Charger",
		"description": "Amaizing Charger, that is very fast.",
		"original_price": 15,
		"discount_percent": 50,
		"final_price": 7.5,
		"stock_quantity": 21,
		"category": [
			"mobile",
			"electronics"
		],
		"images": [
			"/media/users/abebe/products/1/th-1856382654.png",
			"/media/users/abebe/products/1/pexels-stephane-hurbe-4065578.jpg",
			"/media/users/abebe/products/1/mac_bg.jpg"
		],
		"posted_at": "2024-12-27 12:00:00 (AM)"
	},
	"product_stats": {
		"no_of_ratings": 0,
		"rating": 0,
		"no_of_reviews": 1,
		"total_items_sold": 16
	}
}
```
#### `404 Not Found`
```json
{
	"error": "Product does not exist."
}
```

## Purchase a Product
- **URL**: `https://isri21.pythonanywhere.com/products/<id>/`
- **Method**: `POST`
- **Description**: Purchase a product.
### Headers
| Key             | Value              | Description                   |
| --------------- | ------------------ | ----------------------------- |
| `Authorization` | `Token <token>`    | Required for authentication.  |
### Path Parameters
| Parameter | Type  | Required | Description                          |
| --------- | ----- | -------- | ------------------------------------ |
| `{id}`    | `int` | Yes      | The `id` of the product to purchase. |
#### Example path
```https
https://isri21.pythonanywhere.com/products/1/
```
### Body Parameter

| Field      | Type  | Required | Description                             |
| ---------- | ----- | -------- | --------------------------------------- |
| `quantity` | `int` | Yes      | The quantity of the product to purchase |
#### Example Request Body
```json
{
	"quantity": 1
}
```
### Responses
#### `200 Ok`
- If the purchase was successful.
```json
{
    "message": "Purchase Successful",
    "purchase_info": {
        "user": "root",
        "product": "I Phone Charger",
        "purchase_price": 7.5,
        "discount": 50,
        "quantity": 1,
        "purchase_date": "2025-01-01 01:31:40"
    }
}
```
#### `401 Unauthorized`
```json
{
	"authentication_error": "You must be authenticated in order to purchase a product, please send you authentication token in the request header."
}
```
#### `400 Bad Request`
- If no quantity provided.
```json
{
	"quantity": [
		"This field is required."
	]
}
```
- If the quantity specified for purchase is greater than the available stock.
```json
{
    "quantity": [
        "The amount you specified is greater than the available stock. which is {avaliable stock}"
    ]
}
```
- If the quantity specified for purchase is not greater than zero.
```json
{
    "quantity": [
        "Purchase amount must be greater than 0."
    ]
}
```
- If the quantity specified for purchase is not an integer.
```json
{
    "quantity": [
        "A valid integer is required."
    ]
}
```
#### `404 Not Found`
- If the product doesn't exist
```json
{
	"error": "Product does not exist."
}
```
## Get Product Review
**URL**: `https://isri21.pythonanywhere.com/products/{id}/reviews/`
**Method**: `GET`
**Description**: User can get the reviews for a specific product.
### Path Parameters

| Parameter | Type  | Required | Description              |
| --------- | ----- | -------- | ------------------------ |
| `{id}`    | `int` | Yes      | The `id` of the product. |
#### Example Path
```https
https://isri21.pythonanywhere.com/products/7/reviews/
```
### Responses
#### `200 OK`
```json
{
	"count": 2,
	"next": null,
	"previous": null,
	"results": [
		{
			"review_id": "7",
			"user": "root",
			"product": "Shoe",
			"review": "Very comfortable shoes.",
			"review_date": "2025-01-03 13:48:04",
			"edited_at": "2025-01-03 13:48:04"
		},
		{
			"review_id": "9",
			"user": "kebede",
			"product": "Shoe",
			"review": "I don't like it.",
			"review_date": "2025-01-03 15:46:03",
			"edited_at": "2025-01-03 15:46:52"
		}
	]
}
```
#### `404 Not Found`
- If the product does not exists
```json
{
	"error": "Product does not exist."
}
```
- If there are no reviews for the product.
```json
{
	"no_reviews": "There are no reviews for this product."
}
```

## Add a Product to Wishlist
- **URL**: `isri21.pythonanywhere.com/products/{id}/wishlist/`
- **Method**: `POST`
- **Description**: Add a product to a users wish list.
### Header
| Key             | Value              | Description                   |
| --------------- | ------------------ | ----------------------------- |
| `Authorization` | `Token <token>`    | Required for authentication.  |
| `Content-Type`  | `application/json` | Indicates the request format. |
### Path Parameters
| Parameter | Type  | Required | Description                                 |
| --------- | ----- | -------- | ------------------------------------------- |
| `{id}`    | `int` | Yes      | The `id` of the product to add to wish list |
#### Example path
```https
https://isri21.pythonanywhere.com/products/1/wishlist/
```
### Responses
#### `201 Created`
```json
{
	"status": "Product {product name} added to wish list",
}
```
#### `404 Not Found`
```json
{
	"error": "Product does not exist."
}
```

#### `409 Conflict`
```json
{
	"error": "You have already added this product to your wish list."
}
```

#### `401 Unauthorized`
```json
{
	"authentication_error": "You must be authenticated in order to add a product your wish list, please send you authentication token in the request header."
}
```

## Review Product
- **URL**: `https://isri21.pythonanywhere.com/products/{id}/review/`
- **Method**: `POST`
- **Description**: Give a product a review
### Header
| Key             | Value              | Description                   |
| --------------- | ------------------ | ----------------------------- |
| `Authorization` | `Token <token>`    | Required for authentication.  |

### Path Parameters
| Parameter | Type  | Required | Description                               |
| --------- | ----- | -------- | ----------------------------------------- |
| `{id}`    | `int` | Yes      | The `id` of the product to add to review. |
#### Example path
```https
https://isri21.pythonanywhere.com/products/1/review/
```

### Body Parameters
| Parameter | Type  | Required | Description                |
| --------- | ----- | -------- | -------------------------- |
| `review`  | `str` | Yes      | The review for the product |
#### Example Request Body
```json
{
	"review": "This is a very nice product."
}
```
### Responses
#### `201 Created`
```json
{
	"status": "You have successfully reviewed the product."
}
```
#### `403 Forbidden`
```json
{
	"error": "In order to review a product, you must first purchase it."
}
```
#### `404 Not Found`
```json
{
	"error": "Product does not exist."
}
```
#### `409 Conflict`
```json
{
	"error": "You have already reviewed this product."
}
```
#### `401 Unauthorized`
```json
{
	"authentication_error": "You must be authenticated in order to add a product your wish list, please send you authentication token in the request header."
}
```
#### `400 Bad Request`
- If the review field is not specified
```json
{
    "review": [
        "This field is required."
    ]
}
```

## Rate a Product
- **URL**: `https://isri21.pythonanywhere.com/products/{id}/rate/`
- **Method**: `POST`
- **Description**: Give a product a rating
### Header
| Key             | Value              | Description                   |
| --------------- | ------------------ | ----------------------------- |
| `Authorization` | `Token <token>`    | Required for authentication.  |
| `Content-Type`  | `application/json` | Indicates the request format. |
### Path Parameters
| Parameter | Type  | Required | Description                            |
| --------- | ----- | -------- | -------------------------------------- |
| `{id}`    | `int` | Yes      | The `id` of the product to add to rate |
#### Example path
```https
https://isri21.pythonanywhere.com/products/1/review/
```

### Body Parameters
| Parameter | Type  | Required | Description                 |
| --------- | ----- | -------- | --------------------------- |
| `review`  | `str` | Yes      | The review for the product. |
#### Example Request Body
```json
{
	"rating": 5.6
}
```
### Responses
#### `201 Created`
```json
{
	"status": "You have successfully rated the product."
}
```
#### `403 Forbidden`
```json
{
	"error": "In order to rate a product, you must first purchase it."
}
```
#### `404 Not Found`
```json
{
	"error": "Product does not exist."
}
```
#### `409 Conflict`
```json
{
	"error": "You have already rated this product."
}
```
#### `401 Unauthorized`
```json
{
	"authentication_error": "You must be authenticated in order to rate a product. Please send you authentication token in the request header."
}
```
#### `400 Bad Request`
- If the rating field is not specified
```json
{
    "rating": [
        "This field is required."
    ]
}
```
- If the rating field is not a number.
```json
{
    "rating": [
        "A valid number is required."
    ]
}
```
- If the value of the rating is not between 1 and 10
```json
{
	"rating": [
		"Only 2 whole digit are allowed."
	]
}
```
```json
{
	"rating": [
		"Rating can only be between 1 and 10."
	]
}
```

- If the value has more than three digits.
```json
{
	"rating": [
		"Rating can only contain 3 digits."
	]
}
```
- If more than one decimal place in rating. Eg: `3.45`
```json
{
	"rating": [
		"Only 1 decimal place is allowed."
	]
}
```
## Get All Categories
- **URL**: `https://isri21.pythonanywhere.com/categories/`  
- **Method**: `GET`  
- **Description**: View all the available categories.
### Query Parameters

| Parameter  | Type  | Required | Description                                                          | Default | Example        |
| ---------- | ----- | -------- | -------------------------------------------------------------------- | ------- | -------------- |
| `page`     | `int` | No       | Specifying the page number for paginating the products in the store. | `1`     | `?page=2`      |
| `per_page` | `int` | No       | Control the number of product items per page.                        | `5`     | `?page_size=2` |
#### Example Query
```url
https://isri21.pythonanywhere.com/categories/?page=2&per_page=3
```
### Responses
#### `200 OK`
```json
{
	"count": 7,
	"next": "http://isri21.pythonanywhere.com/categories/?page=3",
	"previous": "http://isri21.pythonanywhere.com/categories/",
	"results": [
		{
			"id": 8,
			"creator": "abebe",
			"name": "Vehicle",
			"products_in_category": 0
		},
		{
			"id": 10,
			"creator": "abebe",
			"name": "Chair",
			"products_in_category": 0
		},
		{
			"id": 11,
			"creator": "root",
			"name": "Cotton",
			"products_in_category": 1
		}
	]
}
```

# Profile Endpoints
## Get Profile Details
- **URL**: `https://isri21.pythonanywhere.com/account/profile/`  
- **Method**: `GET`  
- **Description**: View the details of a users profile.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Responses
#### `200 Ok`
```json
{
	"profile_details": {
		"username": "root",
		"first_name": "Root",
		"last_name": "",
		"email": "root@gmail.com"
	},
	"financial_details": {
		"money_spent": "3325.0 ETB",
		"money_earned": "3332.5 ETB"
	},
	"stat": {
		"products_purchased": 9,
		"products_reviewed": 3,
		"products_rated": 1,
		"products_posted": 4,
		"products_in_wishlist": 1,
		"categories_created": 5
	}
}
```
#### `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Update Profile Details
- **URL**: `https://isri21.pythonanywhere.com/account/profile/`  
- **Method**: `PATCH`  
- **Description**: Update the 
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Body Parameters
- At least one of the body parameters must be sent in the request.

| Parameter    | Type     | Required | Description                           |
| ------------ | -------- | -------- | ------------------------------------- |
| `first_name` | `string` | Yes      | Update the first name of the user.    |
| `last_name`  | `string` | Yes      | Update the last name of the user.     |
| `email`      | `string` | Yes      | Update the email address of the user. |
#### Example Response Body
```json
{
	"last_name": "Bikila"
}
```
### Responses
#### `200 Ok`
```json
{
	"status": "Update succesfull.",
	"updated_profile": {
		"username": "root",
		"first_name": "Kinfe",
		"last_name": "Daniel",
		"email": "root@gmail.com"
	}
}
```
#### `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### `404 Not Found`
```json
{
	"error": "User with the username [abebe] does not exist."
}
```
#### `400 Bad Request`
- If not body parameters were passed
```json
{
	"field": "No update fields were specified."
}
```
- If entered an invalid email address
```json
{
    "email": [
        "Enter a valid email address."
    ]
}
```

## Get Products Posted
- **URL**: `https://isri21.pythonanywhere.com/account/products/`
- **Method**: `GET`
- **Description**: User can get a list of all the products that they have posted.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Query Parameters

| Parameter  | Type  | Required | Description                                                          | Default | Example       |
| ---------- | ----- | -------- | -------------------------------------------------------------------- | ------- | ------------- |
| `page`     | `int` | No       | Specifying the page number for paginating the products in the store. | `1`     | `?page=2`     |
| `per_page` | `int` | No       | Control the number of product items per page.                        | `5`     | `?per_page=2` |
#### Example Query
```url
https://isri21.pythonanywhere.com/account/products/?page=2&per_page=3
```
### Response
#### `200 OK`
Returns all the products in the store, or returns the products as specified in the query parameters.
```json
{
	"count": 3,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"name": "I Phone Charger",
			"images": [
				"/media/users/abebe/products/1/th-1856382654.png",
				"/media/users/abebe/products/1/pexels-stephane-hurbe-4065578.jpg",
				"/media/users/abebe/products/1/mac_bg.jpg"
			],
			"category": [
				"Mobile",
				"Electronics"
			],
			"stock_quantity": 27
		},
		{
			"id": 2,
			"name": "Shoe",
			"images": [
				"/media/users/root/products/2/l.jpg"
			],
			"category": [
				"Electronics"
			],
			"stock_quantity": 30
		},
		{
			"id": 3,
			"name": "This is a test",
			"images": [
				"/media/users/abebe/products/3/kl.jpg"
			],
			"category": [
				"Mobile"
			],
			"stock_quantity": 0
		}
	]
}
```
#### `204 No Content`
- If the user has not posted any products
```json
{
	"no_content": "User has not posted any products yet."
}
```
#### `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```
## Create Product
**URL**: `https://isri21.pythonanywhere.com/account/products/`
**Method**: `POST`
**Description**: Users can post a product on the store.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
| `Content-Type`  | `multipart/form-data` | Specifies the request format. |
### Body Parameters

| Field              | Type    | Required | Description                                                                                                                                         | Constraints                                                                                |
| ------------------ | ------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `name`             | `str`   | Yes      | The name of the product.                                                                                                                            |                                                                                            |
| `description`      | `str`   | Yes      | A detailed description of the product.                                                                                                              |                                                                                            |
| `original_price`   | `str`   | Yes      | The price of the product.                                                                                                                           | Positive number                                                                            |
| `discount_percent` | `int`   | Yes      | The percentage of discount on the product. If there is not discount specify `0`                                                                     | Between `1` & `100`                                                                        |
| `stock_quantity`   | `int`   | Yes      | Number of items in stock.                                                                                                                           | Non negative number.                                                                       |
| `category`         | `str`   | Yes      | Category of the product. When uploading multiple categories, make sure to use the same field name for all.                                          | At least one image is required. Can only use categories that have been previously created. |
| `images`           | `image` | Yes      | Image files for the product. We can add multiple images to a product. When uploading multiple images, make sure to use the same field name for all. | At least one image is required.                                                            |
#### Example Request Body
The request is sent as a multiform data. We can use tools like `cURL` or `Postman` to send the request.
#### Example using cURL
```bash
curl -X POST https://isri21.pythonanywhere.com/products/ \
  -H "Authorization: Token asfd998a09asdf098asflakjn" \
  -F "name=Speaker" \
  -F "description=Great Mouse!" \
  -F "original_price=100" \
  -F "discount_percent=20" \
  -F "stock_quantity=78" \
  -F "category=electronics" \
  -F "category=mobile" \
  -F "images=@/path/to/image1.jpg"
  -F "images=@/path/to/image2.jpg"

```

### Responses
#### `201 Created`
The product was posted successfully. Returns the details of the product.
```json
{
	"status": "Successfully Created a New Product!",
	"product": {
		"id": 68,
		"owner": 1,
		"name": "Speaker",
		"description": "Great Mouse!",
		"original_price": 100,
		"discount_percent": 20,
		"final_price": 80,
		"stock_quantity": 78,
		"category": [
			"electronics",
			"mobile"
		],
		"images": [
			"/media/users/root/products/68/th-1856382654.png",
			"/media/users/root/products/68/Screenshot_2024-12-31_235857.png"
		],
		"posted_at": "2025-01-04 00:47:36"
	}
}
```
#### `400 Bad Request`
- If the field was not specified
```json
{
	"name": [
		"This field is required."
	],
	"description": [
		"This field is required."
	],
	"original_price": [
		"This field is required."
	],
	"discount_percent": [
		"This field is required."
	],
	"stock_quantity": [
		"This field is required."
	],
	"category": [
		"This field is required."
	],
	"images": [
		"This field is required."
	]
}
```

- If `original_price` is a negative number
```json
{
	"original_price": [
		"Must be a number greater than 0."
	]
}
```
- If `original_price` is greater than 1,000,000 ETB
```json
{
	"original_price": [
		"Only products with prices not greater than 1,000,000 ETB can be posted on this store."
	]
}
```
- If `discount_percent` is not between 0 and 100.
```json
{
	"discount_percent": [
		"Must be a percentage value between 0 and 100."
	]
}
```
-  If `stock_quantity` is a negative number
```json
{
	"stock_quantity": [
		"Can not be a number less than 0."
	]
}
```
- If `category` doesn't exist.
```json
{
	"category": {
		"Laptop": "This category does not exist. If you want to use it, create it first."
	}
}
```
- If `image` uploaded is of an unsupported type.
```json
{
	"images": {
		"0": [
			"Upload a valid image. The file you uploaded was either not an image or a corrupted image."
		]
	}
}
```
```json
{
	"images": [
		"[Minimal Windows 11.jpg] is not a JPG, JPEG or PNG file."
	]
}
```

#### `401 Unauthorized`
- If the user was not authenticated.
```json
{
	"detail": "Authentication credentials were not provided."
}
```
## Update Product
**URL**: `https://isri21.pythonanywhere.com/account/products/{id}/`
**Method**: `PATCH`
**Description**: Users can edit a product post on the store.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
| `Content-Type`  | `multipart/form-data` | Specifies the request format. |
### Path Parameters
| Parameter | Type  | Required | Description            |
| --------- | ----- | -------- | ---------------------- |
| `id`      | `int` | Yes      | The product to update. |
### Body Parameters
- At least one of the body parameters must be specified.

| Field              | Type    | Required | Description                                                                                                                                         | Constraints                                                                                                              |
| ------------------ | ------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `name`             | `str`   | No       | The name of the product.                                                                                                                            |                                                                                                                          |
| `description`      | `str`   | No       | A detailed description of the product.                                                                                                              |                                                                                                                          |
| `original_price`   | `str`   | No       | The price of the product.                                                                                                                           | Positive number                                                                                                          |
| `discount_percent` | `int`   | No       | The percentage of discount on the product. If there is not discount specify `0`                                                                     | Between `1` & `100`                                                                                                      |
| `stock_quantity`   | `int`   | No       | Number of items in stock.                                                                                                                           | Non negative number.                                                                                                     |
| `categories`       | `str`   | No       | Comma-separated list of category IDs the product belongs to.                                                                                        | The entered as csv's must be ones that have already been created. To get list of created categories go to ***a;lskjdf*** |
| `image`            | `image` | No       | Image files for the product. We can add multiple images to a product. When uploading multiple images, make sure to use the same field name for all. | At least one image is required.                                                                                          |
#### Example Request Body
The request is sent as a multiform data. We can use tools like `cURL` or `Postman` to send the request.
#### Example using cURL
```bash
curl -X PATCH https://isri21.pythonanywhere.com/products/ \
  -H "Authorization: Token asfd998a09asdf098asflakjn" \
  -F "name=Updated Speacker" \
```

### Responses
#### `200 OK`
```json
{
	"status": "Successfully Updated the Product",
	"product": {
		"id": 60,
		"owner": "root",
		"name": "Updated Speaker",
		"description": "Great Speaker!",
		"original_price": 160,
		"discount_percent": 10,
		"final_price": 144,
		"stock_quantity": 65,
		"category": [
			"furniture"
		],
		"images": [
			"/media/users/root/products/60/Screenshot_2024-12-31_235857_18Ttzz2.png",
			"/media/users/root/products/60/Minimal_Windows_11_tJxk8B6.jpg"
		],
		"posted_at": "2025-01-04 12:03:39 (AM)"
	}
}
```
#### `400 Bad Request`
- If `original_price` is a negative number
```json
{
	"original_price": [
		"Must be a number greater than 0."
	]
}
```
- If `original_price` is greater than 1,000,000 ETB
```json
{
	"original_price": [
		"Only products with prices not greater than 1,000,000 ETB can be posted on this store."
	]
}
```
- If `discount_percent` is not between 0 and 100.
```json
{
	"discount_percent": [
		"Must be a percentage value between 0 and 100."
	]
}
```
-  If `stock_quantity` is a negative number
```json
{
	"stock_quantity": [
		"Can not be a number less than 0."
	]
}
```
- If `category` doesn't exist.
```json
{
	"category": {
		"Laptop": "This category does not exist. If you want to use it, create it first."
	}
}
```
- If `image` uploaded is of an unsupported type.
```json
{
	"images": {
		"0": [
			"Upload a valid image. The file you uploaded was either not an image or a corrupted image."
		]
	}
}
```
```json
{
	"images": [
		"[Minimal Windows 11.jpg] is not a JPG, JPEG or PNG file."
	]
}
```

#### `401 Unauthorized`
- If the user was not authenticated.
```json
{
	"detail": "Authentication credentials were not provided."
}
```
## Delete Product
**URL**: `https://isri21.pythonanywhere.com/account/products/{id}/`
**Method**: `DELETE`
**Description**: Delete your product posted.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
### Path Parameters
| Parameter | Type  | Required | Description                      |
| --------- | ----- | -------- | -------------------------------- |
| `id`      | `int` | Yes      | The id of the product to delete. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/account/products/1/
```
### Responses
#### `204 No Content`
- If successfully delete.
#### `404 Not Found`
```json
{
	"error": "Product does not exist."
}
```

#### `401 Unauthorized`
- If token was not sent in the header.
```json
{
	"detail": "Authentication credentials were not provided."
}
```
- When trying to delete a review which you didn't create.
```json
{
	"authorizatoin_error": "Only the owner of the review can manage it."
}
```
## Get Categories by User
- **URL**: `https://isri21.pythonanywhere.com/account/categories/`  
- **Method**: `GET`  
- **Description**: View all categories created by the user.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Responses
#### `200 OK`
```json
{
	"count": 4,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 3,
			"creator": "abebe",
			"name": "Furniture"
		},
		{
			"id": 7,
			"creator": "abebe",
			"name": "Furniture"
		},
		{
			"id": 8,
			"creator": "abebe",
			"name": "Vehicle"
		},
		{
			"id": 9,
			"creator": "abebe",
			"name": "Car"
		}
	]
}
```
#### `204 No Content`
```json
{
	"no_categories": "You have not created any products yet."
}
```
#### `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Create Category
**URL**: `https://isri21.pythonanywhere.com/account/categories/`
**Method**: `POST`
**Description**: Create a new category.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Body Parameters
| Parameter | Type  | Required | Description                        |
| --------- | ----- | -------- | ---------------------------------- |
| `name`    | `str` | Yes      | The name of the category to update |
#### Example Request Body
```json
{
	"name": "Bottle"
}
```
### Responses
#### `200 OK`
```json
{
	"status": "You have successfully created the category.",
	"category": {
		"id": 15,
		"creator": "root",
		"name": "Bottle",
		"products_in_category": 0
	}
}
```
#### `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```
#### `409 Conflict`
```json
{
    "name": "There already exists a category with this name."
}
```

## Update Category
**URL**: `https://isri21.pythonanywhere.com/account/category/{id}/`
**Method**: `PUT`
**Description**: Owner of a category can update the category. Category can only updated if there are no associated products, this is due to security reasons.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
### Path Parameters
| Parameter  | Type  | Required | Description                       |
| ---------- | ----- | -------- | --------------------------------- |
| `id`       | `int` | Yes      | The id of the category to update. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/account/category/12/
```
### Body Parameters
| Parameter | Type  | Required | Description                        |
| --------- | ----- | -------- | ---------------------------------- |
| `name`    | `str` | Yes      | The name of the category to update |
#### Example Request Body
```json
{
	"name": "Mobile"
}
```
### Responses
#### `200 OK`
```json
{
	"status": "You have successfully updated the category.",
	"updated": {
		"id": 12,
		"creator": "root",
		"name": "Mobile",
		"products_in_category": 0
	}
}
```
#### `404 Not Found`
- If category id in path parameter is invalid.
```json
{
	"error": "Category does not exist."
}
```

#### `401 Unauthorized`
- If authentication token not sent in header
```json
{
	"detail": "Authentication credentials were not provided."
}
```
- If trying to update a category created by another user
```json
{
	"authorizatoin_error": "Only the owner of the category can manage it."
}
```
#### `409 Conflict`
```json
{
    "name": "There already exists a category with this name."
}
```
#### `403 Forbidden`
```json
{
	"frobidden": "There are products associated with this category. There for you can not edit it."
}
```

## Delete Category
**URL**: `/account/categories/{id}/`
**Method**: `DELETE`
**Description**: Owner of a category can delete the category. Category can only updated if there are no associated products, this is due to security reasons.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
### Path Parameters
| Parameter  | Type  | Required | Description                       |
| ---------- | ----- | -------- | --------------------------------- |
| `id`       | `int` | Yes      | The id of the category to update. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/profile/category/1/
```
### Responses
#### `204 No Content`
- If successfully delete.
#### `404 Not Found`
- If category id in path parameter is invalid.
```json
{
	"error": "Category does not exist."
}
```
#### `401 Unauthorized`
- If authentication token not sent in header
```json
{
	"detail": "Authentication credentials were not provided."
}
```
- If trying to update a category created by another user
```json
{
	"authorizatoin_error": "Only the owner of the category can manage it."
}
```
#### `403 Forbidden`
```json
{
	"frobidden": "There are products associated with this category. There for you can not edit it."
}
```
## Get User Wishlist
- **URL**: `https://isri21.pythonanywhere.com/account/wishlist/`  
- **Method**: `GET`  
- **Description**: View all the items of the users wishlist.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Responses
#### `200 OK`
```json
[
    {
        "id": 5,
        "product": "I Phone Charger",
        "wishlisted_at": "2025-01-02"
    },
    {
        "id": 6,
        "product": "Shoe",
        "wishlisted_at": "2025-01-02"
    }
]
```
#### `204 No Content`
```json
{
	"no_products": "You have no products in you wishlist."
}
```
#### `401 Unauthorized`
```json
{
	"detail": "Authentication credentials were not provided."
}
```
## Delete Product From Wishlist
**URL**: `https://isri21.pythonanywhere.com/account/wishlist/{id}/`
**Method**: `DELETE`
**Description**: Delete a product from wish list
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Path Parameters
| Parameter  | Type  | Required | Description                       |
| ---------- | ----- | -------- | --------------------------------- |
| `id`       | `int` | Yes      | The id of the category to update. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/profile/wishlist/1/
```
### Responses
#### `204 No Content`
- If successfully delete.
#### `404 Not Found`
- If product id in path parameter is invalid.
```json
{
	"error": "This product is not in your wishlist"
}
```
#### `401 Unauthorized`
```json
{
	"detail": "Authentication credentials were not provided."
}
```
## Get Purchased Items
- **URL**: `https://isri21.pythonanywhere.com/account/purchases/`  
- **Method**: `GET`  
- **Description**: View all the items of the users purchased.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Query Parameters
| Parameter  | Type  | Required | Description                                                          | Default | Example        |
| ---------- | ----- | -------- | -------------------------------------------------------------------- | ------- | -------------- |
| `page`     | `int` | No       | Specifying the page number for paginating the products in the store. | `1`     | `?page=2`      |
| `per_page` | `int` | No       | Control the number of product items per page.                        | `5`     | `?page_size=2` |
### Responses
#### `200 OK`
```json
{
	"count": 5,
	"next": "http://isri21.pythonanywhere.com/account/purchases/?page=2",
	"previous": null,
	"results": [
		{
			"purchase_id": 36,
			"product": "Shoe",
			"discount": 0,
			"purchase_price": 10,
			"quantity": 4,
			"purchase_date": "2025-01-02 01:10:57"
		},
		{
			"purchase_id": 35,
			"product": "I Phone Charger",
			"discount": 50,
			"purchase_price": 7,
			"quantity": 2,
			"purchase_date": "2025-01-02 00:58:59"
		},
		{
			"purchase_id": 34,
			"product": "I Phone Charger",
			"discount": 50,
			"purchase_price": 7,
			"quantity": 2,
			"purchase_date": "2025-01-01 21:08:03"
		}
	]
}
```
#### `204 No Content`
```json
{
	"no_items": "You have no purchased products."
}
```
#### `401 Unauthorized`
```json
{
	"detail": "Authentication credentials were not provided."
}
```

## Get Products Reviewed
- **URL**: `https://isri21.pythonanywhere.com/account/reviews/`  
- **Method**: `GET`  
- **Description**: View all products that a user reviewed.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Responses
#### `200 OK`
```json
{
	"count": 3,
	"next": null,
	"previous": null,
	"results": [
		{
			"product": "I Phone Charger",
			"review": "Cool Product",
			"review_date": "2025-01-01 12:16:46",
			"edited_at": "2025-01-01 12:16:46"
		},
		{
			"product": "Shoe",
			"review": "Very comfortable shoes.",
			"review_date": "2025-01-03 13:48:04",
			"edited_at": "2025-01-03 13:48:04"
		},
		{
			"product": "This is a test",
			"review": "Test review",
			"review_date": "2025-01-03 13:48:33",
			"edited_at": "2025-01-03 13:48:33"
		}
	]
}
```
#### `204 No Content`
```json
{
	"no_reviews": "You have not reviewd any products yet."
}
```
#### `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```
## Update Review
**URL**: `/account/reviews/{id}`
**Method**: `PUT`
**Description**: Update review of a product.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
### Path Parameters
| Parameter | Type  | Required | Description                     |
| --------- | ----- | -------- | ------------------------------- |
| `id`      | `int` | Yes      | The id of the review to update. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/account/reviews/1/
```
### Body Parameters
| Parameter | Type  | Required | Description                        |
| --------- | ----- | -------- | ---------------------------------- |
| `review`  | `str` | Yes      | The updated review of the product. |
#### Example Request Body
```json
{
    "review": "Updated My Review, This is bad product."
}
```
### Responses
#### `200 OK`
```json
{
	"status": "You have succesfully updated your review.",
	"updated_review": {
		"review_id": "6",
		"product": "I Phone Charger",
		"review": "Updated My Review, This is bad product.",
		"review_date": "2025-01-01 12:16:46",
		"edited_at": "2025-01-03 15:36:53"
	}
}
```
#### `404 Not Found`
```json
{
	"error": "Review does not exist."
}
```

#### `401 Unauthorized`
- If token was not sent in the header.
```json
{
	"detail": "Authentication credentials were not provided."
}
```
- When trying to delete a review which you didn't create.
```json
{
	"authorizatoin_error": "Only the owner of the review can manage it."
}
```
## Delete Category
**URL**: `https://isri21.pythonanywhere.com/account/reviews/{id}/`
**Method**: `DELETE`
**Description**: Delete your review of a product.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
### Path Parameters
| Parameter | Type  | Required | Description                     |
| --------- | ----- | -------- | ------------------------------- |
| `id`      | `int` | Yes      | The id of the review to delete. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/account/reviews/1/
```
### Responses
#### `204 No Content`
- If successfully delete.
#### `404 Not Found`
```json
{
	"error": "Review does not exist."
}
```

#### `401 Unauthorized`
- If token was not sent in the header.
```json
{
	"detail": "Authentication credentials were not provided."
}
```
- When trying to delete a review which you didn't create.
```json
{
	"authorizatoin_error": "Only the owner of the review can manage it."
}
```
## Get Products Rated
- **URL**: `https://isri21.pythonanywhere.com/account/ratings/`  
- **Method**: `GET`  
- **Description**: View all products that a user rated.
### Headers
| Key             | Value           | Description                  |
| --------------- | --------------- | ---------------------------- |
| `Authorization` | `Token <token>` | Required for authentication. |
### Responses
#### `200 OK`
```json
{
	"count": 2,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 3,
			"product": "I Phone Charger",
			"ratings": "8.3",
			"rating_date": "2025-01-01 13:56:05",
			"edited_at": "2025-01-03 16:55:26"
		},
		{
			"id": 4,
			"product": "Shoe",
			"ratings": "4.0",
			"rating_date": "2025-01-02 01:11:23",
			"edited_at": "2025-01-02 01:11:23"
		}
	]
}
```
#### `204 No Content`
```json
{
	"no_ratings": "You have not rated any products yet."
}
```
#### `401 Unauthorized`
```json
{
    "detail": "Authentication credentials were not provided."
}
```
## Update Rating
**URL**: `https://isri21.pythonanywhere.com/account/ratings/{id}/`
**Method**: `PUT`
**Description**: Update review of a product.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
### Path Parameters
| Parameter | Type  | Required | Description                     |
| --------- | ----- | -------- | ------------------------------- |
| `id`      | `int` | Yes      | The id of the rating to update. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/account/ratings/1/
```
### Body Parameters
| Parameter | Type  | Required | Description                        |
| --------- | ----- | -------- | ---------------------------------- |
| `rating`  | `str` | Yes      | The updated review of the product. |
#### Example Request Body
```json
{
    "rating": 8.3
}
```
### Responses
#### `200 OK`
```json
{
	"status": "You have succesfully updated your rating.",
	"updated_rating": {
		"id": 3,
		"product": "I Phone Charger",
		"rating": "8.3",
		"rating_date": "2025-01-01 13:56:05",
		"edited_at": "2025-01-03 16:55:26"
	}
}
```
#### `404 Not Found`
```json
{
	"error": "Rating does not exist."
}
```

#### `401 Unauthorized`
- If token was not sent in the header.
```json
{
	"detail": "Authentication credentials were not provided."
}
```
- When trying to delete a review which you didn't create.
```json
{
	"authorizatoin_error": "Only the owner of the rating can manage it."
}
```
#### `400 Bad Request`
- If the rating field is not specified
```json
{
    "rating": [
        "This field is required."
    ]
}
```
- If the rating field is not a number.
```json
{
    "rating": [
        "A valid number is required."
    ]
}
```
- If the value of the rating is not between 1 and 10
```json
{
	"rating": [
		"Only 2 whole digit are allowed."
	]
}
```
```json
{
	"rating": [
		"Rating can only be between 1 and 10."
	]
}
```

- If the value has more than three digits.
```json
{
	"rating": [
		"Rating can only contain 3 digits."
	]
}
```
- If more than one decimal place in rating. Eg: `3.45`
```json
{
	"rating": [
		"Only 1 decimal place is allowed."
	]
}

## Delete Rating
**URL**: `/account/ratings/{id}`
**Method**: `DELETE`
**Description**: Delete your rating of a product.
### Headers
| Key             | Value                 | Description                   |
| --------------- | --------------------- | ----------------------------- |
| `Authorization` | `Token <token>`       | Required for authentication.  |
### Path Parameters
| Parameter | Type  | Required | Description                     |
| --------- | ----- | -------- | ------------------------------- |
| `id`      | `int` | Yes      | The id of the rating to delete. |
#### Example Path Parameter
```https
https://isri21.pythonanywhere.com/account/ratings/1
```
### Responses
#### `204 No Content`
- If successfully delete.
#### `404 Not Found`
```json
{
	"error": "Rating does not exist."
}
```

#### `401 Unauthorized`
- If token was not sent in the header.
```json
{
	"detail": "Authentication credentials were not provided."
}
```
- When trying to delete a review which you didn't create.
```json
{
	"authorizatoin_error": "Only the owner of the rating can manage it."
}
```