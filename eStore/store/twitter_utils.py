"""Twitter integration utilities.

Provides a minimal Twitter OAuth client and helper functions used to
tweet about new stores and products. Credentials are pulled from Django
settings. Functions return booleans and log diagnostic messages.
"""

import requests
from requests_oauthlib import OAuth1Session, OAuth1
import logging
from django.conf import settings
import mimetypes

logger = logging.getLogger(__name__)


class TwitterOAuthClient:
    """Twitter API client using OAuth 1.0a"""

    def __init__(self):
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

        # API endpoints
        self.tweet_url = "https://api.twitter.com/2/tweets"
        self.media_upload_url = (
            "https://upload.twitter.com/1.1/media/upload.json"
        )

    def get_oauth_session(self):
        """Create and return OAuth1Session"""
        return OAuth1Session(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
        )

    def get_oauth1(self):
        """Create and return OAuth1 for requests"""
        return OAuth1(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
        )

    def upload_media(self, image_path):
        """
        Upload media to Twitter.

        Args:
            image_path: Path to the image file

        Returns:
            media_id (str) or None if failed
        """
        try:
            # Read the image file
            with open(image_path, "rb") as file:
                file_data = file.read()

            # Determine media type
            media_type = mimetypes.guess_type(image_path)[0]
            if not media_type:
                media_type = "application/octet-stream"

            # Create OAuth session
            oauth = self.get_oauth1()

            # Prepare the request
            files = {
                "media": (image_path.split("/")[-1], file_data, media_type)
            }

            # Upload media
            response = requests.post(
                self.media_upload_url, files=files, auth=oauth
            )

            if response.status_code == 200:
                media_id = response.json().get("media_id_string")
                logger.info(
                    "Successfully uploaded media. Media ID: %s", media_id
                )
                return media_id
            else:
                logger.error(
                    "Failed to upload media: %s - %s",
                    response.status_code,
                    response.text,
                )
                return None

        except Exception as e:
            logger.error("Error uploading media: %s", e)
            return None

    def create_tweet(self, text, media_ids=None):
        """
        Create a tweet.

        Args:
            text: Tweet text (max 280 characters)
            media_ids: List of media IDs to attach (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare tweet payload
            payload = {"text": text}

            # Add media if provided
            if media_ids:
                payload["media"] = {"media_ids": media_ids}

            # Create OAuth session
            oauth_session = self.get_oauth_session()

            # Make the request
            response = oauth_session.post(
                self.tweet_url,
                json=payload,
            )

            if response.status_code == 201:
                tweet_data = response.json()
                tweet_id = tweet_data.get("data", {}).get("id")
                logger.info(
                    "Successfully created tweet. Tweet ID: %s", tweet_id
                )
                return True
            else:
                logger.error(
                    "Failed to create tweet: %s - %s",
                    response.status_code,
                    response.text,
                )
                return False

        except Exception as e:
            logger.error("Error creating tweet: %s", e)
            return False


def tweet_new_store(store):
    """
    Tweet about a new store creation.

    Args:
        store: Store model instance

    Returns:
        bool: True if successful, False otherwise
    """
    if not settings.ENABLE_TWITTER:
        logger.info("Twitter integration is disabled")
        return False

    try:
        # Create tweet text. Build short fragments first so each source
        # line stays under the flake8 line-length limit.
        if len(store.description) > 100:
            short_desc = store.description[:100] + "..."
        else:
            short_desc = store.description[:100]

        tweet_text = (
            " New Store Alert! \n\n"
            + f" {store.name}\n"
            + f" Owner: {store.owner.username}\n"
            + f" {short_desc}\n\n"
            + "#NewStore #eCommerce #Shopping"
        )

        # Ensure tweet is within character limit (280 characters)
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        # Initialize Twitter client
        twitter_client = TwitterOAuthClient()

        # Upload logo if available
        media_ids = []
        if store.logo:
            try:
                media_id = twitter_client.upload_media(store.logo.path)
                if media_id:
                    media_ids.append(media_id)
                    logger.info("Uploaded logo for store: %s", store.name)
            except Exception as e:
                logger.warning(
                    "Failed to upload logo, posting without image: %s",
                    e,
                )

        # Create tweet
        success = twitter_client.create_tweet(
            tweet_text, media_ids if media_ids else None
        )

        if success:
            logger.info("Successfully tweeted about new store: %s", store.name)
        else:
            logger.error("Failed to tweet about store: %s", store.name)

        return success

    except Exception as e:
        logger.error("Error in tweet_new_store: %s", e)
        return False


def tweet_new_product(product):
    """
    Tweet about a new product addition.

    Args:
        product: Product model instance

    Returns:
        bool: True if successful, False otherwise
    """
    if not settings.ENABLE_TWITTER:
        logger.info("Twitter integration is disabled")
        return False

    try:
        # Create tweet text. Keep each literal/source line short.
        if len(product.description) > 80:
            short_desc = product.description[:80] + "..."
        else:
            short_desc = product.description[:80]

        tweet_text = (
            " New Product Available! \n\n"
            + f" Store: {product.store.name}\n"
            + f" Product: {product.name}\n"
            + f" Price: R{product.price}\n"
            + f" {short_desc}\n\n"
            + "#NewProduct #Shopping #eCommerce"
        )

        # Ensure tweet is within character limit
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        # Initialize Twitter client
        twitter_client = TwitterOAuthClient()

        # Upload image if available
        media_ids = []
        if product.image:
            try:
                media_id = twitter_client.upload_media(product.image.path)
                if media_id:
                    media_ids.append(media_id)
                    logger.info("Uploaded image for product: %s", product.name)
            except Exception as e:
                logger.warning(
                    "Failed to upload image, posting without image: %s",
                    e,
                )

        # Create tweet
        success = twitter_client.create_tweet(
            tweet_text, media_ids if media_ids else None
        )

        if success:
            logger.info(
                "Successfully tweeted about new product: %s",
                product.name,
            )
        else:
            logger.error(
                "Failed to tweet about product: %s",
                product.name,
            )

        return success

    except Exception as e:
        logger.error("Error in tweet_new_product: %s", e)
        return False
