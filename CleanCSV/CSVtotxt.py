import ast

import pandas as pd


def get_and_become_text_data(input_file, text_file):
    df = pd.read_csv(input_file)
    for index, row in df.iterrows():
        addresses = ast.literal_eval(row['address'])
        address = ', '.join([item.replace('_', ' ') for item in addresses])
        if address == 'Other':
            address = 'etc.'
        menus = ast.literal_eval(row['menu'])
        menu = ', '.join([item.replace('_', ' ') for item in menus])
        if menu == 'No bakery related menu':
            menu = 'Unknown'
        delivery_hr = row['delivery_hr']
        if type(delivery_hr) is float:
            delivery_hr = 'Unknown'
        scale = row['price_scale']
        if scale == 'none':
            scale = 'Unknown'
        elif scale == "3":
            scale = 'expensive'
        elif scale == "2":
            scale = 'average'
        elif scale == "1":
            scale = 'cheap'
        try:
            seats = int(row['seat_amt'])
        except ValueError:
            seats = 'Unknown'
        car_park = row['car_park']
        if not isinstance(car_park, float):
            if car_park:
                car_park = 'car park.'
            else:
                car_park = 'no car park.'
        else:
            car_park = 'no car park information'
        wifi = row['wi_fi']
        if not isinstance(wifi, float):
            if wifi:
                wifi = 'Wi-Fi'
            else:
                wifi = 'no Wi-FI'
        else:
            wifi = 'no Wi-Fi information'
        pet = row['pet_allows']
        if not isinstance(pet, float):
            if pet:
                pet = 'allows pet'
            else:
                pet = 'not allows pet'
        else:
            pet = 'unsure about pet allowance'
        card = row['card_accept']
        if not isinstance(card, float):
            if card:
                card = 'accept credit card transaction'
            else:
                card = 'not accept credit card'
        else:
            card = 'no information on credit card acceptance'
        delivery = row['delivery']
        if not isinstance(delivery, float):
            if delivery:
                delivery = 'has delivery option'
            else:
                delivery = 'no delivery'
        else:
            delivery = 'unsure about delivery information'
        kid = row['for_kids']
        if not isinstance(kid, float):
            if kid:
                kid = 'suitable for children'
            else:
                kid = 'not suitable for children'
        else:
            kid = 'the suitability for children is unclear'
        group = row['for_group']
        if not isinstance(group, float):
            if group:
                group = 'suitable for group'
            else:
                group = 'not suitable for group'
        else:
            group = 'the suitability for group is unclear.'
        reviews = ast.literal_eval(row['review'])
        if reviews != ['no review']:
            review = [' '.join(item) for item in reviews]
            review = list(set(review))
            review = (item.lower() for item in review)
            review = (item.replace('_', ' ') for item in review)
            review = ', '.join(review)
        else:
            review = 'no review so far'
        rating = row['rating']
        print(rating)
        checkin = row['check_in']
        bookmark = row['bookmarked']
        string = (f"{index+1}. {row['name']}\nrating mean: {rating} There are {row['rating_amt']} people(s) rated this bakery shop/restaurant"
              f"\nThere are {checkin} people(s) check in and {bookmark} people(s) bookmark this location."
              f"\nThis bakery shop/restaurant located in: {address}"
              f"\nThis particular shop/restaurant sells {menu}"
              f"\nThe price on their menu are {scale}"
              f"\nThis bakery shop/restaurant open hour is {row['open_hr']}"
              f"\nThis bakery shop/restaurant delivery hour is {delivery_hr}"
              f"\nThis bakery shop/restaurant has {seats} seats for customer."
              f"\nPeople review that this bakery shop/restaurant food, service, and atmosphere are {review}."
              f"\nThis shop service detail are:\nThey have {car_park}, {wifi}, {card}, and {delivery}."
              f"\nThis shop availability detail are:\nThey {pet}, {kid}, and {group}.\n")
        with open(text_file, "a") as file:
            file.write(string)
if __name__ == '__main__':
    get_and_become_text_data('../Material/cleaned_bakery.csv', '../Material/csv_detail.txt')