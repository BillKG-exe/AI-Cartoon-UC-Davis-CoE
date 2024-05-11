if __name__ == "__main__":
    # Import the necessary modules
    from test import TransferStyle
    import os

    # Set the image and save paths
    image_path = r"dataset\test0\2014-08-27_00-00-08_UTC.jpg"
    save_dir = "results"

    # Create the save directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Create an instance of TransferStyle
    transfer = TransferStyle()

    # Call the transfer_style method of TransferStyle
    transfer.transfer_style(145, image_path, save_dir)

    print("Image processed and saved successfully.")
