Name:             foo
Epoch:            1
Version:          1.2.3
Release:          42%{?dist}
Summary:          Some package

Group:            Development/Languages
License:          ASL 2.0
URL:              http://pypi.python.org/pypi/%{name}
Source1:          http://pypi.python.org/packages/source/f/%{name}/%{name}-%{version}.tar.gz

%description
This is foo!

%prep
%setup -q

%changelog
* Mon Apr 07 2014 John Foo <jfoo@redhat.com> 1.2.3-42
- Update to upstream 1.2.3

* Tue Mar 25 2014 John Foo <jfoo@redhat.com> 1.2.2-1
- Update to upstream 1.2.2
