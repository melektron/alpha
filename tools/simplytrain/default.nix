{
  python313Packages,
  #el_std_py,
  typed-argument-parser,
  lib
}:

python313Packages.buildPythonApplication 
{
  pname = "simplytrain";
  version = "1.0.0";
  src = ./.;

  propagatedBuildInputs = with python313Packages; [
    flask
    waitress
    typed-argument-parser
  ];

  pyproject = true;
  build-system = [
    python313Packages.setuptools
    python313Packages.setuptools-scm
    python313Packages.wheel
  ];

  meta = with lib; {
    description = "Quick-n-dirty vocabulary translation training server with bare-bones webinterface.";
    homepage = "https://github.com/melektron/alpha";
    platforms = platforms.all;
    mainProgram = "simplytrain";
  };
}
