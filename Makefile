.PHONY: all
all: test

.PHONY: test
test:
	@GOEXPERIMENT=cgocheck2 go test -v -cover -covermode=atomic ./...

.PHONY: ci
ci:
	@GOEXPERIMENT=cgocheck2 go test -v -cover -covermode=atomic -coverprofile=coverage.txt ./...

.PHONY: calibrate_valid
calibrate_valid:
	@go test -v -calibrate -run TestValidCalibration

.PHONY: calibrate_is_ascii
calibrate_is_ascii:
	@go test -v -calibrate -run TestIsASCIICalibration

.PHONY: calibrate
calibrate: calibrate_valid calibrate_is_ascii

.PHONY: clean
clean:
	@go clean
