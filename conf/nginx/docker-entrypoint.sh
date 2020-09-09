#!/bin/sh

set -e

gunicorn -c agmt/main:app