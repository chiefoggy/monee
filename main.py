#imports required libraries
from bs4 import BeautifulSoup
import requests
import smtplib
from email.message import EmailMessage

# Function to extract Product Title
def get_title(soup):
    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id":'productTitle'})

        # Title as a string value
        title_string = title.text.strip()
    except AttributeError:
        title_string = "Product name unavaliable"
    return title_string

# Function to extract Product Price
def get_price(soup):
    try:
        price = soup.find("span", attrs={'id':'priceblock_ourprice'}).string.strip()
    except AttributeError:
        try:
            # If there is some deal price
            price = soup.find("span", attrs={'id':'priceblock_dealprice'}).string.strip()
        except:     
            price = "Price unavaliable"
    return price

# Function to extract Product Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
            rating = float(rating.split()[0])
        except:
            rating = 0.0
    return rating

# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()
    except AttributeError:
        review_count = 0
    return review_count

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id':'availability'})
        available = available.find("span").string.strip()
    except AttributeError:
        available = "Not Available"
    return available 

def send_email(receiver_email, email_body):
    # set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # Edit line 65 and 66 with your password and email address 
    password = 'YOUR_PASSWORD'
    sender_email = 'YOUR_EMAIL'
    server.login(sender_email, password)

    # create the email message
    message = EmailMessage()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Email Subject Line'
    message.set_content(email_body)

    # send the email
    server.send_message(message)

    # close the SMTP server
    server.quit()

if __name__ == '__main__':

    # Greet the user
    print("Welcome to Monee!")
    
    # Ask the user for a search term
    search_term = input("Please enter a search term: ")

    # Manipulate the search term to be used as part of the link
    search_term = search_term.replace(" ", "+")

    # The webpage URL
    URL = f"https://www.amazon.com/s?k={search_term}&ref=nb_sb_noss_2"
    
    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US'})
    
    # HTTP Request
    webpage = requests.get(URL, headers=HEADERS)

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")

    # Fetch links as List of Tag Objects
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})

    # Store the links
    links_list = []

    # Loop for extracting links from Tag Objects
    for link in links:
        links_list.append(link.get('href'))

    # Store product data
    product_data = []

    # Loop for extracting product details from each link 
    for link in links_list:

        new_webpage = requests.get("https://www.amazon.com" + link, headers=HEADERS)

        new_soup = BeautifulSoup(new_webpage.content, "lxml")
        
        # Get product details and store them in a dictionary
        product_details = {
            "title": get_title(new_soup),
            "price": get_price(new_soup),
            "rating": get_rating(new_soup),
            "review_count": get_review_count(new_soup),
            "availability": get_availability(new_soup)
        }

        # Add product details to product_data list
        product_data.append(product_details)

    # Print product data
    '''
    for product in product_data:
        print("Product Title =", product["title"])
        print("Product Price =", product["price"])
        print("Product Rating =", product["rating"])
        print("Number of Product Reviews =", product["review_count"])
        print("Availability =", product["availability"])
        print()
        print()
    '''
    # Ask the user if they want to receive an email with the product data
    send_email_confirmation = input("Would you like to receive an email with the product data? (y/n): ")

    if send_email_confirmation == "y":

        # Ask the user for their email address
        email_address = input("Please enter your email address: ")

        # Set up the email message
        message = f"You have requested for an email summary of the product {search_term}. "

        for product in product_data:
            message += f"Product Title: {product['title']}\n"
            message += f"Product Price: {product['price']}\n"
            message += f"Product Rating: {product['rating']}\n"
            message += f"Number of Product Reviews: {product['review_count']}\n"
            message += f"Availability: {product['availability']}\n"
            message += "\n"
        
        message += "Thank you for using Monee!"
        
        body = message

        # Send the email
        send_email(email_address, body)

        print("Email sent!")
    else:
        for product in product_data:
            print(f"Product Title: {product['title']}\n")
            print(f"Product Price: {product['price']}\n")
            print(f"Product Rating: {product['rating']}\n")
            print(f"Number of Product Reviews: {product['review_count']}\n")
            print(f"Availability: {product['availability']}\n")
            print()

#web scraper stops working as Amazon blocks frequent web scraping
if product_data == []: 
    print("You have tried too many times! Please try again later.")

print("Thank you for using Monee!") 
