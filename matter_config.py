#!/usr/bin/env python3
"""
General-purpose Matter device attribute configuration tool.
This script allows you to read and write any attribute on any Matter device
via the Matter server client library.
"""

import argparse
import asyncio
import logging
import sys

import aiohttp
from matter_server.client.client import MatterClient

# Default Configuration
# Common Matter server URLs:
# - Home Assistant add-on (internal): ws://localhost:5580/ws
# - Home Assistant add-on (external): ws://[HA_IP]:5580/ws
# - Standalone server: ws://[SERVER_IP]:5580/ws
MATTER_SERVER_URL = "ws://homeassistant.local:5580/ws"  # Default Matter server WebSocket URL

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



async def read_attribute_value(client: MatterClient, node_id: int, endpoint_id: int, cluster_id: int, attribute_id: int) -> int | None:
    """Read an attribute value from a Matter device."""
    try:
        # Create attribute path string
        attribute_path = f"{endpoint_id}/{cluster_id}/{attribute_id}"
        logger.debug(f"Reading attribute {attribute_path} from node {node_id}")

        # Use the client's read_attribute method
        result = await client.read_attribute(node_id, attribute_path)

        if result is not None:
            logger.debug(f"Successfully read attribute {attribute_path}: {result}")

            # Extract the actual value from the result dictionary
            if isinstance(result, dict) and attribute_path in result:
                actual_value = result[attribute_path]
                logger.debug(f"Extracted value: {actual_value}")
                return actual_value
            else:
                # If result is not a dict or doesn't contain expected key, return as-is
                logger.debug(f"Result is not a dict or doesn't contain expected key, returning as-is: {result}")
                return result
        else:
            logger.error(f"Failed to read attribute {attribute_path}: No result returned")
            return None

    except Exception as e:
        logger.error(f"Error reading attribute {endpoint_id}/{cluster_id}/{attribute_id}: {e}")
        return None


async def write_attribute_value(client: MatterClient, node_id: int, endpoint_id: int, cluster_id: int, attribute_id: int, value: int) -> bool:
    """Write an attribute value to a Matter device."""
    try:
        # Create attribute path string
        attribute_path = f"{endpoint_id}/{cluster_id}/{attribute_id}"
        logger.debug(f"Writing value {value} to attribute {attribute_path} on node {node_id}")

        # Use the client's write_attribute method
        await client.write_attribute(node_id, attribute_path, value)

        logger.info(f"Successfully wrote value {value} to attribute {attribute_path}")
        return True

    except Exception as e:
        logger.error(f"Error writing attribute {endpoint_id}/{cluster_id}/{attribute_id}: {e}")
        return False
    

async def configure_attribute_value(new_value: int, node_id: int, endpoint_id: int, cluster_id: int, attribute_id: int, server_url: str) -> bool:
    """Configure a Matter device attribute."""

    logger.info("=" * 60)
    logger.info("Matter Device Attribute Configuration")
    logger.info("=" * 60)
    logger.info("Connecting to Matter server...")

    try:
        async with aiohttp.ClientSession() as session:
            async with MatterClient(server_url, session) as client:
                # Connect and start listening
                connect_event = asyncio.Event()
                asyncio.create_task(client.start_listening(connect_event))
                await connect_event.wait()
                logger.info("Connected to Matter server")

                # Skip node info check - proceed directly to attribute operations
                logger.info(f"Proceeding with node {node_id}...")

                # Read current attribute value
                logger.info("Reading current attribute value...")
                current_value = await read_attribute_value(
                    client, node_id, endpoint_id, cluster_id, attribute_id
                )

                if current_value is not None:
                    logger.info(f"Current attribute value: {current_value}")
                else:
                    logger.warning("Could not read current attribute value, proceeding anyway...")

                # Write new attribute value
                logger.info(f"Setting attribute to {new_value}...")
                success = await write_attribute_value(
                    client, node_id, endpoint_id, cluster_id, attribute_id, new_value
                )

                if not success:
                    return False

                # Verify the change
                logger.info("Verifying the change...")
                await asyncio.sleep(2)  # Give the device a moment to process

                verified_value = await read_attribute_value(
                    client, node_id, endpoint_id, cluster_id, attribute_id
                )

                if verified_value is not None:
                    if verified_value == new_value:
                        logger.info(f"✓ Successfully configured attribute to {verified_value}!")
                        logger.info("The device attribute has been updated.")
                        return True
                    else:
                        logger.warning(f"Attribute was set but shows unexpected value: {verified_value} (expected {new_value})")
                        return False
                else:
                    logger.warning("Could not verify the new attribute value")
                    return False

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure Matter device attributes via the Matter server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for missing values)
  python3 matter_config.py

  # All positional arguments (node-id endpoint-id cluster-id attribute-id attribute-value [url])
  python3 matter_config.py 3 1 1030 3 30
  python3 matter_config.py 3 1 1030 3 30 ws://192.168.1.100:5580/ws

  # Partial arguments (will prompt for missing ones)
  python3 matter_config.py 3 1 1030
        """
    )

    # Only positional arguments - no -- options
    parser.add_argument('node_id', nargs='?', type=int, help='Matter node ID')
    parser.add_argument('endpoint_id', nargs='?', type=int, help='Endpoint ID')
    parser.add_argument('cluster_id', nargs='?', type=int, help='Cluster ID')
    parser.add_argument('attribute_id', nargs='?', type=int, help='Attribute ID')
    parser.add_argument('attribute_value', nargs='?', type=int, help='New attribute value (1-65535)')
    parser.add_argument('url', nargs='?', type=str, default=MATTER_SERVER_URL,
                       help=f'Matter server WebSocket URL (default: {MATTER_SERVER_URL})')

    return parser.parse_args()


def get_user_input(prompt: str) -> int:
    """Get user input with validation."""
    while True:
        try:
            user_input = input(f"{prompt}: ").strip()

            if not user_input:
                print("Value is required. Please enter a number.")
                continue

            value = int(user_input)
            return value

        except ValueError:
            print("Please enter a valid number.")


async def main():
    """Main function with CLI arguments and interactive configuration."""

    # Parse command line arguments
    args = parse_arguments()

    print("Matter Device Attribute Configuration Tool")
    print("=" * 50)
    print()
    print("This tool allows you to configure Matter device attributes")
    print("via the Matter server client library.")
    print()
    print("Note: Make sure the Matter Server add-on is running in Home Assistant.")
    print("If connection fails, you may need to:")
    print("  1. Go to Settings → Add-ons → Matter Server → Configuration")
    print("  2. Under 'Network', add port 5580 to expose the WebSocket")
    print("  3. Restart the Matter Server add-on")
    print()

    # Get configuration values (from CLI args or user input)
    node_id = args.node_id if args.node_id is not None else get_user_input("Enter Matter node ID")
    endpoint_id = args.endpoint_id if args.endpoint_id is not None else get_user_input("Enter endpoint ID")
    cluster_id = args.cluster_id if args.cluster_id is not None else get_user_input("Enter cluster ID")
    attribute_id = args.attribute_id if args.attribute_id is not None else get_user_input("Enter attribute ID")
    attribute_value = args.attribute_value if args.attribute_value is not None else get_user_input("Enter desired attribute value")

    print()
    print(f"Configuration:")
    print(f"  Matter Server URL: {args.url}")
    print(f"  Node ID: {node_id}")
    print(f"  Endpoint ID: {endpoint_id}")
    print(f"  Cluster ID: {cluster_id}")
    print(f"  Attribute ID: {attribute_id}")
    print(f"  Attribute Value: {attribute_value}")
    print()

    print(f"\nAttempting to set attribute to {attribute_value}...")
    print("This will change the device attribute value.")
    print()

    # Confirm the action
    confirm = input("Continue? (y/N): ").strip().lower()
    if not confirm.startswith('y'):
        print("Operation cancelled.")
        return

    # Perform the configuration
    success = await configure_attribute_value(attribute_value, node_id, endpoint_id, cluster_id, attribute_id, args.url)

    if success:
        print("\n" + "=" * 50)
        print("✓ Configuration completed successfully!")
        print(f"Device attribute should now be set to {attribute_value}.")
        print("You may need to wait a few minutes for the change to take effect.")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("✗ Configuration failed!")
        print("Please check the logs above for error details.")
        print("Common issues:")
        print("  - Matter server not running or not accessible")
        print("  - Incorrect node/endpoint/cluster/attribute IDs")
        print("  - Device doesn't support this attribute")
        print("  - Network connectivity issues")
        print("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

