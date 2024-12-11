if [[ $(which python) == *"metric-metadata-service"* ]]; then
  "$@"
else
  poetry run "$@"
fi
exit $?