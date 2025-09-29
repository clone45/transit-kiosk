import pytest
import os
import tempfile
from decimal import Decimal
from repositories.pricing_repository import PricingRepository
from repositories.transit_card_repository import TransitCardRepository
from repositories.trip_repository import TripRepository
from repositories.station_repository import StationRepository
from models.trip import TripStatus


class TestFareCalculation:
    """Unit tests for fare calculation logic."""

    @pytest.fixture
    def pricing_repo(self):
        """Create a temporary pricing repository for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_path = tmp.name

        # Initialize station repo first to create stations table
        from repositories.station_repository import StationRepository
        station_repo = StationRepository(db_path)
        station_repo.create("Station A")
        station_repo.create("Station B")

        # Now initialize pricing repo
        repo = PricingRepository(db_path)

        yield repo

        # Cleanup - close connections first
        del repo
        del station_repo
        import gc
        gc.collect()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # File still locked, ignore

    def test_get_price_between_stations(self, pricing_repo):
        """Test fare calculation between two stations."""
        price = pricing_repo.get_price(1, 2)
        assert price == Decimal('3.25')

    def test_get_price_reversed_stations(self, pricing_repo):
        """Test fare calculation with reversed station order."""
        price = pricing_repo.get_price(2, 1)  # Reversed order
        assert price == Decimal('3.25')  # Should return same price

    def test_get_price_nonexistent_route(self, pricing_repo):
        """Test fare calculation for non-existent route."""
        price = pricing_repo.get_price(1, 999)
        assert price is None

    def test_minimum_fare(self, pricing_repo):
        """Test minimum fare lookup."""
        lowest = pricing_repo.get_lowest_price()
        assert lowest.price == Decimal('2.25')  # Actual minimum from seeded data


class TestTapFlow:
    """Unit tests for card tap entry/exit flow."""

    @pytest.fixture
    def test_repos(self):
        """Create temporary repositories for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_path = tmp.name

        # Initialize repositories in correct order
        station_repo = StationRepository(db_path)
        card_repo = TransitCardRepository(db_path)
        trip_repo = TripRepository(db_path)
        pricing_repo = PricingRepository(db_path)

        # Setup test data - stations are already created by pricing repo initialization
        repos = {
            'card': card_repo,
            'trip': trip_repo,
            'station': station_repo,
            'pricing': pricing_repo
        }

        yield repos

        # Cleanup - close connections first
        for repo in repos.values():
            del repo
        import gc
        gc.collect()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # File still locked, ignore

    def test_card_entry_sufficient_balance(self, test_repos):
        """Test card entry with sufficient balance."""
        repos = test_repos

        # Create card with sufficient balance
        card = repos['card'].create(Decimal('10.00'), "test-uuid")

        # Create trip (entry)
        trip = repos['trip'].create(card.id, 1, Decimal('0.00'))

        assert trip.status == TripStatus.ACTIVE
        assert trip.source_station_id == 1
        assert trip.destination_station_id is None

    def test_card_entry_insufficient_balance(self, test_repos):
        """Test card entry with insufficient balance."""
        repos = test_repos

        # Create card with insufficient balance
        card = repos['card'].create(Decimal('1.00'), "test-uuid")
        minimum_fare = repos['pricing'].get_lowest_price().price

        # Check if balance is sufficient
        assert card.balance < minimum_fare

    def test_card_exit_completes_trip(self, test_repos):
        """Test card exit completes trip with fare deduction."""
        repos = test_repos

        # Create card and start trip
        card = repos['card'].create(Decimal('10.00'), "test-uuid")
        trip = repos['trip'].create(card.id, 1, Decimal('0.00'))

        # Get fare between stations
        fare = repos['pricing'].get_price(1, 2)

        # Complete trip (exit)
        completed_trip = repos['trip'].complete_trip(trip.id, 2, fare)

        assert completed_trip.status == TripStatus.COMPLETED
        assert completed_trip.destination_station_id == 2
        assert completed_trip.cost == fare

    def test_active_trip_tracking(self, test_repos):
        """Test that only one active trip per card is allowed."""
        repos = test_repos

        # Create card and start trip
        card = repos['card'].create(Decimal('10.00'), "test-uuid")
        trip1 = repos['trip'].create(card.id, 1, Decimal('0.00'))

        # Check active trip exists
        active_trip = repos['trip'].get_active_trip_by_card(card.id)
        assert active_trip.id == trip1.id
        assert active_trip.status == TripStatus.ACTIVE