%define major 0
%define libname %mklibname md %{major}
%define devname %mklibname -d md

%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%if %{with compat32}
%define lib32name libmd%{major}
%define dev32name libmd-devel
%endif

%global optflags %{optflags} -O3

# (tpg) enable PGO build
%bcond_without pgo

Summary:	Message digest functions from BSD systems
Name:		libmd
Version:	1.0.4
Release:	2
License:	BSD-2-Clause OR BSD-3-Clause OR ISC OR SUSE-Public-Domain
Group:		System/Libraries
Url:		https://www.hadrons.org/software/libmd/
Source0:	https://archive.hadrons.org/software/libmd/%{name}-%{version}.tar.xz

%description
The libmd library provides a few message digest ("hash") functions, as
found on various BSDs on a library with the same name and with a compatible
API.

%package -n %{libname}
Summary:	Provides message digest functions from BSD systems
Group:		System/Libraries

%description -n %{libname}
The libmd library provides a few message digest ("hash") functions, as
found on various BSDs on a library with the same name and with a compatible
API.

Digests supported: MD2/4/5, RIPEMD160, SHA1, SHA2-256/384/512.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Development files for the %{name} library.

%if %{with compat32}
%package -n %{lib32name}
Summary:	Provides message digest functions from BSD systems (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
The libmd library provides a few message digest ("hash") functions, as
found on various BSDs on a library with the same name and with a compatible
API.

Digests supported: MD2/4/5, RIPEMD160, SHA1, SHA2-256/384/512.

%package -n %{dev32name}
Summary:	Development files for %{name} (32-bit)
Group:		Development/C
Requires:	%{devname} = %{EVRD}
Requires:	%{lib32name} = %{EVRD}

%description -n %{dev32name}
Development files for the %{name} library (32-bit).
%endif

%prep
%autosetup -p1

%build
export CONFIGURE_TOP=$(pwd)
%if %{with compat32}
mkdir build32
cd build32
%configure32
cd ..
%endif

mkdir build
cd build
%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%configure
%make_build

make check

unset LD_LIBRARY_PATH
llvm-profdata merge --output=%{name}-llvm.profdata *.profraw
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw
make clean

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
%configure

cd ..

%if %{with compat32}
%make_build -C build32
%endif
%make_build -C build

%install
%if %{with compat32}
%make_install -C build32
%endif
%make_install -C build

%files -n %{libname}
%{_libdir}/libmd.so.%{major}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%doc %{_mandir}/man3/*.3*

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libmd.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/libmd.so
%{_prefix}/lib/pkgconfig/*.pc
%endif
