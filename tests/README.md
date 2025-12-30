# Testing guide

This project uses pytest with pytest-describe for Jest-like nested test structure.

The nested structure allows for clear organization of tests and scenarios, at the same time it helps cover all possible scenarios.

Sample test structure (in Jest):

```javascript
describe('agent', () => {
    describe('when there are failures detected', () => {
        describe('and there is a single node failure', () => {
            describe('and there is a crew available', () => {
                beforeEach(() => {
                    db.when(getCrew).resolve(["crew a"]);
                });

                it('should plan something', () => {
                    ...
                });
            });
            
            describe('but there is no crew available', () => {
            ...
            })
        })
    })
})
```

## Running tests

### Run all tests

```bash
uv run pytest
```

### Run only unit tests

```bash
uv run pytest tests/unit
```

### Run only end-to-end tests

```bash
uv run pytest tests/e2e
```

## Test structure

Tests follow a nested describe pattern similar to Jest:

```python
def describe_component():
    """Top-level test suite for a component."""
    
    def describe_method():
        """Tests for a specific method."""
        
        def describe_when_condition():
            """Context: specific condition or scenario."""
            
            @pytest.fixture
            def setup():
                # Setup for this context
                return SomeObject()
            
            def it_should_behave_correctly(setup):
                # Test implementation
                assert setup.method() == expected
```

This creates a test path like:

```
describe_component::describe_method::describe_when_condition::it_should_do_something
```

Tests are separated into two categories:
- `unit`: Tests for individual components in isolation
- `e2e`: End-to-end tests for integration and workflow validation

## Naming conventions

- `describe_*`: Groups related tests (like Jest's `describe`)
- `it_*` or `should_*`: Individual test cases (like Jest's `it`)
- `when_*`: Can also be used for test names to describe conditions
- Use fixtures for setup/teardown within describe blocks

## Fixtures

Define fixtures at any level of nesting:

```python
def describe_when_user_logged_in():
    @pytest.fixture
    def logged_in_user():
        return User(authenticated=True)
    
    def it_should_access_dashboard(logged_in_user):
        assert logged_in_user.can_access_dashboard()
```
