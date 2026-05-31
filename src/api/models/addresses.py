from dataclasses import dataclass



@dataclass
class Address:
    host: str
    port: int

@dataclass
class RedisConfig:
    address: Address