import logging
import grpc
from concurrent import futures

from .proto.eligibility import eligibility_pb2_grpc
from .proto.claims import claims_pb2_grpc
from .proto.greeter import greeter_pb2_grpc
from .services import EligibilityService, ClaimsService, GreeterServicer

from care_gateway.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    eligibility_pb2_grpc.add_EligibilityServiceServicer_to_server(
        EligibilityService(), server
    )
    claims_pb2_grpc.add_ClaimsServiceServicer_to_server(
        ClaimsService(),
        server,
    )
    greeter_pb2_grpc.add_GreeterServiceServicer_to_server(
        GreeterServicer(),
        server,
    )

    server.add_insecure_port("[::]:50052")
    logger.info(
        "gRPC server listening on port 50052 with Eligibility and Claims services..."
    )
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
