#!/usr/bin/env python3
import asyncio

from app.motor_simulator import MotorSimulator


async def main():
    simulator = MotorSimulator(record_interval=10.0)
    try:
        await simulator.run()
    except KeyboardInterrupt:
        print("Motor simulator stopped by user")


if __name__ == "__main__":
    asyncio.run(main())
