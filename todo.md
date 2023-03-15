# Todo

- [ ] Build automated tests
  - API tests (integration):
    - Test an entire container, perhaps with an in-memory database?
      - In that case, it needs to be started with a special testing config
      - docker-compose has a special sut-block that can be used to define a testing
          container
  - How are the tests going to be run? What are we testing?
  - Unit tests
    - More resource efficient, could be executed on the application container itself
      during development
    - https://docs.aiohttp.org/en/stable/testing.html

- [ ] Freeze dependencies
- [ ] Migrate to FastAPI
- [ ] Add DELETE /polls/{poll_id} endpoint
- [ ] 
